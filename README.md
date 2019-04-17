# onshape-xblock
Validate Onshape Elements according to a wide range of checks. 

## Installation
To install the xblock on the edx lms and cms, follow the instructions 
[here](https://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/dogwood/configuration/install_xblock.html) and then [here](https://edx.readthedocs.io/projects/open-edx-building-and-running-a-course/en/latest/exercises_tools/enable_exercises_tools.html#enable-additional-exercises-and-tools).
Here is the [link to the pypi repo with the distribution.](https://pypi.org/project/onshape-xblock/)

## Developer Installation
### Setting Up The Environment
This XBlock uses pipenv to manage python packages and npm to manage the frontend packages. To make changes to both the front end and backend, you'll need both installed. Once you've confirmed both are installed, you can install the local dependencies with `npm install --dev` and `pipenv install --dev`.
### Debugging In PyCharm
To debug in pycharm, you should have the xblock sdk set up and running locally. Then, just add a run configuration that points to `<xblock_development_repo>/xblock-sdk` and passes the parameter `runserver`
### Building the Frontend
To build the js from the ts that defines the frontend, simply run `npm run build`