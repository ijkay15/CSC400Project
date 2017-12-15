# CSC400Project
Files for 
For the CSC400 project, my files are all contained in the project folder. The project folder was built in the Cloud SDK folder downloaded from Google Cloud. This allowed connection to Google Cloud services through the Google Cloud command line Shell. There was also a Cloud_Proxy_SQL application in the Cloud SDK folder for connecting the local machine to the Cloud SQL Instance. The flask folder containing the flask library located in the project file was not included due to size. Another folder holding many Google APIs for various parts of the project were also omitted due to size. If needed please let me know. The project folder includes the following files and folders:
- app.yaml for App Engine deployment
- requirements.txt for Google Cloud
- two client_secret.json objects used for authorization to connect to Google Cloud services
- main.py and config.py for initialization
- flask folder for flask library
- reportForms.py for writing report info and pdfWriter.py to create pdfs
- website folder for main website files and subfolers
The website folder contains:
- the model_cloudsql.py file for SQLAlchemy & Cloud SQL
- the __init__.py for the website constructor
- the templates folder, which contain all the html files
- static folder, which contains:
- this contains a css subfolder, images subfolder for static images, and several other static images for use in the website
