#If not in container - set workdir to current file directory
import os
if not 'AM_I_IN_A_DOCKER_CONTAINER' in os.environ:
    os.chdir(os.path.dirname(__file__))

#Include control class and instantiate
from GCE_helpers import GCE_control
GCE = GCE_control()


#Kill VM when script ends - whether that is due to exception or success
import atexit
atexit.register(GCE.kill_vm)

#Redirect stdout and stderr to file, particularly for error messages. This is included in the final status email if SMTP is set up correctly (if you don't want that, best just delete these rows here)
import sys
path = 'stdout.txt'
sys.stdout = open(path, 'w')
sys.stderr = sys.stdout


#Use functions to send update emails and save objects as required
#GCE.save_output("anything") #Saves any object as pickle to Cloud Storage
#GCE.send_email_update("I'm fine") #Sends email update based on config data

#Your code here

GCE.send_email_update('Code within Docker Container launched successfully on Google Compute Engine')
GCE.save_output("Hi")
