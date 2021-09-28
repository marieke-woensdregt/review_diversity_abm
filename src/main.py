import configparser
import pickle
from google.cloud import storage

#Kill VM when script ends
from helpers import *
import atexit
atexit.register(kill_vm)

def create_or_get_bucket(bucket_name):
  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)
  if (bucket.exists()):
      return storage_client.get_bucket(bucket_name)
  else:    
    return storage_client.create_bucket(bucket, location="us")

def save_output(out, filename = "script_output.pkl"):
    bucket = create_or_get_bucket(BUCKET_NAME)

    with open(filename, 'wb') as file:
        pickle.dump(out, file)
        file.close()
    
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)

if __name__ == '__main__':

    config = configparser.ConfigParser()
    config.read("config.conf")
    PROJECT_NAME = config["Config"]["PROJECT_NAME"]
    BUCKET_NAME = config["Config"]["BUCKET_NAME"]

    print('Code within Docker Container launched successfully on Google Compute Engine')

    save_output("banana joe")
