from flask_restful import Resource, reqparse
from flask import request
from sqlalchemy import or_

from models.models import db, User, UserStats, FriendRequest, Habit, HabitCompletion
from services.solr_service import index_user
from services.solr_service import delete_document



user_update_parser = reqparse.RequestParser()
user_update_parser.add_argument("name", type=str, required=True, help="Nome é obrigatório")
user_update_parser.add_argument("email", type=str, required=True, help="Email é obrigatório")
user_update_parser.add_argument("password", type=str, required=False)  
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
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        parser.add_argument("email", required=True)
        parser.add_argument("password", required=True)
        parser.add_argument("avatar", required=False)
        args = parser.parse_args()

        existing = User.query.filter_by(email=args["email"]).first()
        if existing:
            return {"message": "Email já cadastrado"}, 409

        user = User(
            name=args["name"],
            email=args["email"],
            avatar=args.get("avatar")
        )
        user.set_password(args["password"])

        db.session.add(user)
        db.session.commit()  
        index_user(user)

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

        if data["email"] != user.email:
            existing = User.query.filter_by(email=data["email"]).first()
            if existing:
                return {"message": "Email já cadastrado"}, 409

        user.name = data["name"]
        user.email = data["email"]
        user.avatar = data.get("avatar")
        
        if data.get("password"):
            user.set_password(data["password"])

        db.session.commit()
        return {"message": "Usuário atualizado"}, 200

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"message": "Usuário não encontrado"}, 404

        try:
            # 1. Deletar solicitações de amizade (onde o usuário é sender ou receiver)
            friend_requests = FriendRequest.query.filter(
                (FriendRequest.sender_id == user_id) | 
                (FriendRequest.receiver_id == user_id)
            ).all()
            
            for request in friend_requests:
                db.session.delete(request)
            
            # 2. Deletar completions de hábitos
            completions = HabitCompletion.query.filter_by(user_id=user_id).all()
            for completion in completions:
                db.session.delete(completion)
            
            # 3. Deletar hábitos do usuário
            habits = Habit.query.filter_by(user_id=user_id).all()
            for habit in habits:
                db.session.delete(habit)
            
            # 4. Deletar estatísticas do usuário
            if user.stats:
                db.session.delete(user.stats)
            
            # 5. Por fim, deletar o usuário
            db.session.delete(user)
            
            # Commit todas as alterações
            db.session.commit()
            
            # Remover do Solr
            user_solr_id = f"user_{user.id}"
            delete_document("users", user_solr_id)
            
            return {"message": "Usuário deletado com sucesso"}, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar usuário: {e}")
            return {"message": f"Erro ao deletar usuário: {str(e)}"}, 500


class UserSearchResource(Resource):
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