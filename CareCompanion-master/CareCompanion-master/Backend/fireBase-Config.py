import firebase_admin
from firebase_admin import credentials

# Initialize Firebase
cred = credentials.Certificate("C:\Project\Backend\fireBase-Config.py") # Path to your downloaded key
firebase_admin.initialize_app(cred)