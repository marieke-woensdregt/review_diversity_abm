# Easily run a Python script on Google Cloud

Sometimes, data science projects exceed a laptop's capacity. While there are very helpful tools to allow one to run Notebooks online, there does not seem to be a straight-forward way to run a one-off script online. Here my notes - primarily to my future self - on how to do that.

Many thanks to
- https://github.com/jankrynauw/gcp-pycharm-docker
- https://github.com/aminelemaizi/docker-gcp-ml

## Step 1: Prepare script

The quickest way to set up Python with the required dependencies on a Google Cloud Virtual Machine, and to get all necessary code and data there, is to package all of that in a Docker image. 

For that, you just need to add all your requirements to `requirements.txt` (if they cannot be installed with pip, you need to edit the `Dockerfile` directly to install them). Then you need to include your code in main.py, leaving the first 20 lines intact. At the end of the code, use one or more calls to `GCE.save_output()` to save your results. At that point - or throughout the process - you can send yourself update emails using `GCE.send_email_update()`

### Set config parameters

In config.conf, enter the project name and the desired Cloud Storage bucket (folder) name. You might also want to insert SMTP server details to be able to receive status email updates. See this note on using Gmail ^[Gmail seems to work well, but you will likely need to create an [App Password](https://myaccount.google.com/apppasswords) to bypass two-factor authentification.]

## Step 2: Set up Google Cloud and a project

You need a Google Cloud account with billing enabled. There are [offers with generous free trial credit](https://cloud.google.com/free) available. Create a project - best through the browser-based [Console](https://console.cloud.google.com/). Then [install the SDK](https://cloud.google.com/sdk/docs/install) to continue on the command line.

### Set up project

Authenticate gcloud in your terminal, and *select/create a new project* at the end (I use Powershell, which influences some details in this code)

  gcloud init

If you just created a new project, you need to *set up billing* for it. First find out your billing account number, then add it to the project (this will install the SDK *beta* commands and take a while - you can also do it in the visual console if you don't plan to use this often)

  gcloud beta billing accounts list
  gcloud beta billing projects link $PROJECT_ID --billing-account $BILLING_ACCOUNT_ID

*Enable required services.* We need compute to run the VM, cloudbuild to create the Docker file and containerregistry to store

  gcloud services enable compute cloudbuild.googleapis.com containerregistry.googleapis.com

### Build the Docker container

Set up Cloud Build to create the Docker Images whenever you push to the Github repo (or only when you push a specific tag, if you prefer that) - this needs to be done in the browser-based [Console](https://console.cloud.google.com/cloud-build/dashboard). Select that you want to build from Dockerfile (rather than Autodetected) so that you can edit the *Image name* - remove any variables (such as $COMMIT_SHA) and replace them by :latest, so that you can have a stable image name. You can then click on Run to build the first Docker image. Under Build Artefacts, you can find the link to the container registry, where you can copy the link to your image (with a button at the end of the path). It should look something like:

  gcr.io/test-project-329910/github.com/lukaswallrich/pyscript2gce

If you have used the tag latest in the previous step, you can add that to this link to have a stable name for the latest build.

You can also [build the image manually and push it to the container registry](https://cloud.google.com/container-registry/docs/pushing-and-pulling)

## Step 3: Run code

To run the code, you will create a Virtual Machine, giving it any name not currently taken within your project, and providing the link to the image on Container Registry.

When it comes to machine type, there are [many choices](https://cloud.google.com/compute/docs/general-purpose-machines), depending on the RAM and CPU cores required. You will also need to choose a region, `us-central1-b` currently makes sense as US-central is cheap and low in carbon emissions. If your script creates large outputs, or run any other file operations, you will need to increase the boot disk size.

*NB:* Backticks are powershell code to run multi-line code.

  gcloud compute instances create-with-container $INSTANCE_NAME `
    --container-image=gcr.io/test-project-329910/github.com/lukaswallrich/pyscript2gce:latest `
    --zone=us-central1-b `
    --machine-type=n1-standard-1  `
    --boot-disk-size=10GB `
    --scopes cloud-platform `
    --container-restart-policy=never

The virtual machine *should* automatically shut down as soon as the script is done. However, please check that in order to avoid unnecessary costs.

(You can also experiment with pre-emptible machines. They are at least 60% cheaper, but might be pre-empted at any time. For that, add `--preemptible` to the code)

### Get results

Download results from bucket

    gsutil cp -r gs://<bucket-name>/ ./

## Limitations / future improvements

- Set up up project through SDK rather than visual Console would be great. Currently fails because billing account does not get associated.
- Logging could be improved - currently only stdout is captured per email