from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# Banco
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/habitos"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ JWT (obrigatório para @jwt_required funcionar)
app.config["JWT_SECRET_KEY"] = "super-secret-change-me"  # troque depois por algo seguro
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # dev: não expira

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
