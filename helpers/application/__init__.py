from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)

# Config do Banco
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@db:3306/habitos")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT (@jwt_required)
app.config["JWT_SECRET_KEY"] = "super-secret-change-me" #Chave secreta
app.config["JWT_TOKEN_LOCATION"] = ["headers"]  # Onde encontrar o token
app.config["JWT_HEADER_NAME"] = "Authorization"  # Nome do header
app.config["JWT_HEADER_TYPE"] = "Bearer" # Tipo de token
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  

jwt = JWTManager(app)

# CORS
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:3000"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

api = Api(app)
