# Easily run a Python script on Google Cloud

Sometimes, data science projects exceed a laptop's capacity. While there are very helpful tools to allow one to run Notebooks online, there does not seem to be a straight-forward way to run a one-off script online. Here my notes - primarily to my future self - on how to do that.

Many thanks to
- https://github.com/jankrynauw/gcp-pycharm-docker
- https://github.com/aminelemaizi/docker-gcp-ml

## Step 1: Prepare Docker container

The quickest way to set up Python with the required dependencies on a Google Cloud Virtual Machine, and to get all necessary code and data there, is to package all of that in a Docker image. 

### Ensure Google Cloud Access

### Consider automatic building with Cloud Build

You can build the Docker container manually on your machine, which might be best for one-off projects. Alternatively,

## Step 2: Set up Google Cloud

Install SDK (or do everything through the console - but that is not much fun if you do this more than once)

Set up project

Set up bucket for storage

    gsutil mb -b on -p <your-gcp-project-id> gs://<bucket-name>


gcloud compute --project={{__PROJECT_NAME__}} instances create-with-container instance-1 \
  --zone=us-east1-b \
  --machine-type=n1-standard-1  \
  --service-account=686502984651-compute@developer.gserviceaccount.com \
  --image=cos-stable-68-10718-86-0 \
  --image-project=cos-cloud \
  --boot-disk-size=10GB \
  --boot-disk-type=pd-standard \
  --boot-disk-device-name=instance-1 \
  --container-image=gcr.io/sandbox-docker/test:r1.2 \
  --container-restart-policy=always \
  --container-env=MY_PARAMETER=myvalue123

Download results from bucket

    gsutil cp gs://<bucket-name>/ ./