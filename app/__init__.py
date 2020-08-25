from flask import Flask
from flask_cors import CORS
from flask_restful import Api
app = Flask(__name__)
CORS(app)
API = Api(app)
    
from app import api