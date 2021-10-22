# Easily run a Python script on Google Cloud

Sometimes, data science projects exceed a laptop's capacity. While there are very helpful tools to allow one to run Notebooks online, there does not seem to be a straight-forward way to run a one-off script online. Here my notes - primarily to my future self - on how to do that.

Many thanks to
- https://github.com/jankrynauw/gcp-pycharm-docker
- https://github.com/aminelemaizi/docker-gcp-ml

## Step 1: Prepare script

The quickest way to set up Python with the required dependencies on a Google Cloud Virtual Machine, and to get all necessary code and data there, is to package all of that in a Docker image. 

For that, you just need to add all your requirements to `requirements.txt` (if they cannot be installed with pip, you need to edit the `Dockerfile` directly to install them). Then you need to include your code in main.py, leaving the first 12 rows intact. At the end of the code, use one or more calls to `GCE.save_output()` to save your results. At that point - or throughout the process - you can send yourself update emails using `GCE.send_email_update()`

## Set up Google Cloud

### Install SDK (or do everything through the interactive Console - but that is not much fun if you do this more than once)

### Set up project

### Set up cloud build

You can also build manually and 

### Set config parameters

In config.conf, enter the project name and the desired Cloud Storage bucket (folder) name. You might also want to insert SMTP server details to be able to receive status email updates. See this note on using Gmail ^[Gmail seems to work well, but you will likely need to create an [App Password](https://myaccount.google.com/apppasswords) to bypass two-factor authentification.]

## Run code and get results

To run the code, you will create a Virtual Machine. There are many choices, depending on the RAM and CPU cores required. (You can experiment with pre-emptible machines. They are much cheaper, but might be pre-empted at any time.)

*NB:* Backticks are powershell code to run multi-line code.

  gcloud compute --project=python-run-327415 instances create-with-container instance-12 `
    --zone=us-east1-b `
    --machine-type=n1-standard-1  `
    --boot-disk-size=10GB `
    --scopes cloud-platform `
    --container-image=gcr.io/python-run-327415/github.com/lukaswallrich/pyscript2gce:latest `
    --container-restart-policy=never

The virtual machine *should* automatically shut down as soon as the script is done. However, please check that in order to avoid unnecessary costs.

Download results from bucket

    gsutil cp gs://<bucket-name>/ ./


## Set up email status updates

Particularly for long-running scripts, it might be good to get status updates. This is most convenient by email. You can do that with Gmail, but 