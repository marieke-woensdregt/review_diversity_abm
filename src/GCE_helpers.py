import configparser
import pickle
from google.cloud import storage

class GCE_control:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.conf")
        self.PROJECT_NAME = config["Config"]["PROJECT_NAME"]
        self.BUCKET_NAME = config["Config"]["BUCKET_NAME"]
        self.gcepy_smtp_config = config["SMTP"]
        self.output_counter = 0

    def kill_vm(self):
        """
        If we are running inside a GCE VM, kill it.
        """
        print("Trying to kill VM")
        # from https://stackoverflow.com/a/52811140/10581449
        import json
        import logging
        import requests

        # get the token
        r = json.loads(
            requests.get("http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token",
                        headers={"Metadata-Flavor": "Google"})
                .text)

        token = r["access_token"]

        # get instance metadata
        # based on https://cloud.google.com/compute/docs/storing-retrieving-metadata
        project_id = requests.get("http://metadata.google.internal/computeMetadata/v1/project/project-id",
                                headers={"Metadata-Flavor": "Google"}).text

        name = requests.get("http://metadata.google.internal/computeMetadata/v1/instance/name",
                            headers={"Metadata-Flavor": "Google"}).text

        zone_long = requests.get("http://metadata.google.internal/computeMetadata/v1/instance/zone",
                                headers={"Metadata-Flavor": "Google"}).text
        zone = zone_long.split("/")[-1]

        # shut ourselves down
        logging.info("Calling API to delete this VM, {zone}/{name}".format(zone=zone, name=name))

        requests.delete("https://www.googleapis.com/compute/v1/projects/{project_id}/zones/{zone}/instances/{name}"
                        .format(project_id=project_id, zone=zone, name=name),
                        headers={"Authorization": "Bearer {token}".format(token=token)})

    def send_email_update(self, message, subject = "Update on GCE Python Script"):
        import smtplib
        try:
            with smtplib.SMTP(self.gcepy_smtp_config["SERVER"],self.gcepy_smtp_config["PORT"]) as s:
                s.starttls()
                s.login(self.gcepy_smtp_config["LOGIN"], self.gcepy_smtp_config["PWD"])
                s.sendmail(self.gcepy_smtp_config["SENDER_EMAIL"], self.gcepy_smtp_config["RECEIVER_EMAIL"], "Subject: " + subject + "\n\n" + message)
        except Exception as e:
            # Print any error messages to stdout
            print(e)

    def create_or_get_bucket(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.BUCKET_NAME)
        if (bucket.exists()):
            return storage_client.get_bucket(self.BUCKET_NAME)
        else:    
            return storage_client.create_bucket(bucket, location="us")

    def save_output(self, out, filename = None):
        bucket = self.create_or_get_bucket(self.BUCKET_NAME)

        self.output_counter += 1    
        if filename is None:
            filename("script_output_" + self.output_counter + ".pkl")

        if not filename[-4:] == ".pkl":
            filename += ".pkl"    

        with open(filename, 'wb') as file:
            pickle.dump(out, file)
            file.close()
        
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)        