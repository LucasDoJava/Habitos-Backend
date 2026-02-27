from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from models.models import User


class LoginResource(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return {"message": "email e password são obrigatórios"}, 400

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password): # checa o hash fornecido com a senha
            return {"message": "Credenciais inválidas"}, 401

        # criar o token de acesso
        access_token = create_access_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar": user.avatar
            }
        }, 200
