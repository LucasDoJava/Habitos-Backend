from flask_restful import Resource, reqparse
from models.models import db, User

user_parser = reqparse.RequestParser()
user_parser.add_argument("name", type=str, required=True, help="Nome é obrigatório")
user_parser.add_argument("email", type=str, required=True, help="Email é obrigatório")
user_parser.add_argument("password", type=str, required=True, help="Senha é obrigatória")
user_parser.add_argument("avatar", type=str)

class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"message": "Usuário não encontrado"}, 404
            return {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "avatar": user.avatar,
                "created_at": user.created_at.isoformat()
            }
        users = User.query.all()
        return [{"id": u.id, "name": u.name, "email": u.email} for u in users]

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        parser.add_argument("email", required=True)
        parser.add_argument("password", required=True)
        args = parser.parse_args()

        # Cria o usuário
        user = User(
            name=args["name"],
            email=args["email"],
        )
        user.set_password(args["password"]) 

        db.session.add(user)
        db.session.commit()

        return {"message": "Usuário criado com sucesso!"}, 201

    def put(self, user_id):
        data = user_parser.parse_args()
        user = User.query.get(user_id)
        if not user:
            return {"message": "Usuário não encontrado"}, 404
        user.name = data["name"]
        user.email = data["email"]
        user.password = data["password"]
        user.avatar = data.get("avatar")
        db.session.commit()
        return {"message": "Usuário atualizado"}

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "Usuário não encontrado"}, 404
        db.session.delete(user)
        db.session.commit()
        return {"message": "Usuário deletado"}
