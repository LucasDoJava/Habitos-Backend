from flask_restful import Resource, reqparse
from models.models import db, User, UserStats

# Parser para UPDATE (PUT) - senha opcional
user_update_parser = reqparse.RequestParser()
user_update_parser.add_argument("name", type=str, required=True, help="Nome é obrigatório")
user_update_parser.add_argument("email", type=str, required=True, help="Email é obrigatório")
user_update_parser.add_argument("password", type=str, required=False)  # opcional no PUT
user_update_parser.add_argument("avatar", type=str, required=False)


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
            }, 200

        users = User.query.all()
        return [{"id": u.id, "name": u.name, "email": u.email} for u in users], 200

    def post(self):
        # Parser para CREATE (POST) - senha obrigatória
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        parser.add_argument("email", required=True)
        parser.add_argument("password", required=True)
        parser.add_argument("avatar", required=False)
        args = parser.parse_args()

        # evitar email duplicado
        existing = User.query.filter_by(email=args["email"]).first()
        if existing:
            return {"message": "Email já cadastrado"}, 409

        # 1) cria usuário
        user = User(
            name=args["name"],
            email=args["email"],
            avatar=args.get("avatar")
        )
        user.set_password(args["password"])

        db.session.add(user)
        db.session.commit()  # precisa do commit pra ter user.id

        # 2) cria stats padrão pro usuário
        stats_existing = UserStats.query.filter_by(user_id=user.id).first()
        if not stats_existing:
            default_stats = UserStats(
                user_id=user.id,
                level=1,
                total_points=0,
                current_exp=0,
                exp_to_next_level=100,
                achievements={},
                longest_streak=0,
                total_habits_completed=0
            )
            db.session.add(default_stats)
            db.session.commit()

        return {"message": "Usuário criado com sucesso!", "id": user.id}, 201

    def put(self, user_id):
        data = user_update_parser.parse_args()

        user = User.query.get(user_id)
        if not user:
            return {"message": "Usuário não encontrado"}, 404

        # se trocar email, evitar colisão
        if data["email"] != user.email:
            existing = User.query.filter_by(email=data["email"]).first()
            if existing:
                return {"message": "Email já cadastrado"}, 409

        user.name = data["name"]
        user.email = data["email"]
        user.avatar = data.get("avatar")

        # só altera senha se vier no request
        if data.get("password"):
            user.set_password(data["password"])

        db.session.commit()
        return {"message": "Usuário atualizado"}, 200

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "Usuário não encontrado"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": "Usuário deletado"}, 200
