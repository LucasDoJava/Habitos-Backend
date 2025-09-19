from flask import Flask
from flask_restful import Api

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost:3306/habits"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

api = Api(app)
