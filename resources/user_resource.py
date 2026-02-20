from flask_restful import Resource, reqparse
from flask import request
from sqlalchemy import or_

from models.models import db, User, UserStats
from services.solr_service import index_user
from services.solr_service import delete_document


# Parser para UPDATE (PUT) - senha opcional
user_update_parser = reqparse.RequestParser()
user_update_parser.add_argument("name", type=str, required=True, help="Nome é obrigatório")
user_update_parser.add_argument("email", type=str, required=True, help="Email é obrigatório")
user_update_parser.add_argument("password", type=str, required=False)  # opcional no PUT
user_update_parser.add_argument("avatar", type=str, required=False)


def _serialize_user_basic(u: User):
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "avatar": getattr(u, "avatar", None),
    }


class UserResource(Resource):
    def get(self, user_id=None):
        if user_id:
            user = User.query.get(user_id)
            if not user:
                return {"message": "Usuário não encontrado"}, 404

            payload = _serialize_user_basic(user)
            if getattr(user, "created_at", None):
                payload["created_at"] = user.created_at.isoformat()

            return payload, 200

        users = User.query.all()
        return {"users": [_serialize_user_basic(u) for u in users]}, 200

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
        index_user(user)

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

        user_solr_id = f"user_{user.id}"

        db.session.delete(user)
        db.session.commit()

        delete_document("users", user_solr_id)

        return {"message": "Usuário deletado"}, 200


class UserSearchResource(Resource):
    """
    GET /users/search?q=texto
    Retorna usuários filtrando por name ou email (sem Solr).
    """
    def get(self):
        q = (request.args.get("q") or "").strip()
        if not q:
            return {"users": []}, 200

        like = f"%{q}%"
        users = User.query.filter(
            or_(
                User.name.ilike(like),
                User.email.ilike(like)
            )
        ).limit(20).all()

        return {"users": [_serialize_user_basic(u) for u in users]}, 200
