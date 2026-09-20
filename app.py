import os
from flask import Flask
from backend.models import *
from backend.api_controllers import api

app = None

def init_app():
    houseservices_app = Flask(__name__)
    houseservices_app.debug = True
    houseservices_app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///houseservices.db'

    houseservices_app.secret_key = 'mysecretkey'

    # Configure the upload folder
    upload_folder_path = os.path.join(os.getcwd(), 'uploads')  # This will create an 'uploads' folder in the current directory
    houseservices_app.config['UPLOAD_FOLDER'] = upload_folder_path
    houseservices_app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

    # Check if the upload folder exists, if not, create it
    if not os.path.exists(upload_folder_path):
        os.makedirs(upload_folder_path)
        print(f"Created upload folder at: {upload_folder_path}")

    houseservices_app.app_context().push()
    db.init_app(houseservices_app)
    api.init_app(houseservices_app)
    print("Household_services app initialized")
    return houseservices_app

app = init_app()
from backend.controllers import *

if __name__ == "__main__":
    app.run()
