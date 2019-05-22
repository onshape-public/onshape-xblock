# onshape-xblock
Validate Onshape Elements according to a wide range of checks. 

## Installation
To install the xblock on the edx lms and cms, follow the instructions 
[here](https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/dogwood/configuration/install_xblock.html) and then [here](https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/latest/exercises_tools/enable_exercises_tools.html#enable-additional-exercises-and-tools).
Here is the [link to the pypi repo with the distribution.](https://pypi.org/project/onshape-xblock/)

For the bitnami stack, go to the application, and enter the following commands:
```bash
sudo /opt/bitnami/use_edx
source /opt/bitnami/apps/edx/venvs/edxapp/bin/activate
pip install -U onshape_xblock --no-cache-dir
sudo /opt/bitnami/ctlscript.sh restart apache

```

To access the logs, `tail -f /opt/bitnami/apps/edx/var/log/lms/edx.log`

## Using the XBlock
To properly authenticate students who use the xblock, we use OAuth. This is how we're able to get the permissions to check a document on behalf of a student. This authentication procedure happens lazily - the user is only directed through the authentication flow when they submit a request that requires it AND the xblock doesn't currently have the permissions. From the course creator side, they have to do a few setup steps to create the OAuth application in Onshape, and tell it the url at which the xblock will accept validation.

## Developer Installation
### Setting Up The Environment
This XBlock uses pipenv to manage python packages and npm to manage the frontend packages. To make changes to both the front end and backend, you'll need both installed. Once you've confirmed both are installed, you can install the local dependencies with `npm install --dev` and `pipenv install --dev`.
### Debugging In PyCharm
To debug in pycharm, you should have the xblock sdk set up and running locally. Then, just add a run configuration that points to `<xblock_development_repo>/xblock-sdk` and passes the parameter `runserver`
### Building the Frontend
To build the js from the ts that defines the frontend, simply run `npm run build`. This will put the output js into the dist folder and continue to watch the ts for additional changes, rebuilding as necessary. Very often, when you run into issues, they are related to the fact that the runtime expects the implemented js functionality to use the window object for all object names. Therefore, very often within typescript you need to set or get some object from the window object like so: `(<any>window).MyVeryImportantObject`. This should only be necessary when interacting with the js runtime.

## Access the admin
In order to access the admin console, you need to make an ssh tunnel as described here: https://docs.bitnami.com/oci/apps/edx/administration/access-edx-services/
In short (you may need to change some of the defined vars):

```bash
SOURCE_PORT=1234
DESTINATION_PORT=80
KEYFILE=~/.bash/bitnami-google-bitnami-onshape-edx.pem
SERVER_IP=35.188.211.229
sudo ssh -N -L $SOURCE_PORT:127.0.0.1:$DESTINATION_PORT -i $KEYFILE bitnami@$SERVER_IP
```

Then go to: http://localhost:1234/admin/

