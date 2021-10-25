import configparser
import pickle
from google.cloud import storage
import os

class GCE_control:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read("config.conf")
        self.BUCKET_NAME = config["Config"]["BUCKET_NAME"]
        self.gcepy_smtp_config = config["SMTP"]
        if config.has_option("Config", "FILE_PREFIX"):
            self.PREFIX = str(config["Config"]["FILE_PREFIX"])
        else:
            self.PREFIX = ""
        self.output_counter = 0
        if not 'AM_I_IN_A_DOCKER_CONTAINER' in os.environ:
            pass
        else:
            # from https://stackoverflow.com/a/52811140/10581449
            import json
            self.PROJECT_ID = requests.get("http://metadata.google.internal/computeMetadata/v1/project/project-id",
                                    headers={"Metadata-Flavor": "Google"}).text

    def kill_vm(self):

        if os.path.isfile("stdout.txt"):
            with open("stdout.txt", "r") as f:
                logs = "Stdout was:\n" + f.read()
        else:
            logs = ""     
        self.send_email_update("Finished script - trying to kill VM" + "\n" + logs)
        
        #Only try to kill if we are actually in a Docker - not in local testing.
        if not 'AM_I_IN_A_DOCKER_CONTAINER' in os.environ:
            pass
        else:
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


            name = requests.get("http://metadata.google.internal/computeMetadata/v1/instance/name",
                                headers={"Metadata-Flavor": "Google"}).text

            zone_long = requests.get("http://metadata.google.internal/computeMetadata/v1/instance/zone",
                                    headers={"Metadata-Flavor": "Google"}).text
            zone = zone_long.split("/")[-1]

            # shut ourselves down
            logging.info("Calling API to delete this VM, {zone}/{name}".format(zone=zone, name=name))

            requests.delete("https://www.googleapis.com/compute/v1/projects/{self.PROJECT_ID}/zones/{zone}/instances/{name}"
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
            print(e) # Will probably get lost in Docker limbo ...

    def create_or_get_bucket(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.BUCKET_NAME)
        if (bucket.exists()):
            return storage_client.get_bucket(self.BUCKET_NAME)
        else:    
            return storage_client.create_bucket(bucket, location="us", project=self.PROJECT_ID)

    def save_output(self, out, filename = None):
        bucket = self.create_or_get_bucket()

        self.output_counter += 1    
        if filename is None:
            filename = "script_output_" + str(self.output_counter) + ".pkl"

        if not filename[-4:] == ".pkl":
            filename += ".pkl"    

        filename = self.PREFIX + filename    

        with open(filename, 'wb') as file:
            pickle.dump(out, file)
            file.close()
        
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)

        os.remove(filename)
