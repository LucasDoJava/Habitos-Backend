from flask_restful import Resource, reqparse
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import db, UserStats

# OBS:
# - O parser abaixo é usado para POST/PUT (admin/uso manual).
# - Para o endpoint /stats/me (real do usuário logado), não precisa enviar user_id.

stats_parser = reqparse.RequestParser()
stats_parser.add_argument("user_id", type=int, required=True)
stats_parser.add_argument("level", type=int)
stats_parser.add_argument("total_points", type=int)
stats_parser.add_argument("current_exp", type=int)
stats_parser.add_argument("exp_to_next_level", type=int)
stats_parser.add_argument("achievements", type=dict)
stats_parser.add_argument("longest_streak", type=int)
stats_parser.add_argument("total_habits_completed", type=int)


def serialize_stats(stats: UserStats):
    return {
        "id": stats.id,
        "user_id": stats.user_id,
        "level": stats.level,
        "total_points": stats.total_points,
        "current_exp": stats.current_exp,
        "exp_to_next_level": stats.exp_to_next_level,
        "achievements": stats.achievements,
        "longest_streak": stats.longest_streak,
        "total_habits_completed": stats.total_habits_completed
    }


def get_or_create_stats_for_user(user_id: int) -> UserStats:
    """Busca stats do usuário; se não existir, cria com valores padrão."""
    stats = UserStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = UserStats(
            user_id=user_id,
            level=1,
            total_points=0,
            current_exp=0,
            exp_to_next_level=100,
            achievements={},
            longest_streak=0,
            total_habits_completed=0
        )
        db.session.add(stats)
        db.session.commit()
    return stats


class StatsResource(Resource):
    def get(self, stats_id=None):
        # /stats/<id>
        if stats_id is not None:
            stats = UserStats.query.get(stats_id)
            if not stats:
                return {"message": "Stats não encontrado"}, 404
            return serialize_stats(stats), 200

        # /stats?user_id=1  (mantido por compatibilidade)
        user_id = request.args.get("user_id", type=int)
        if user_id is not None:
            stats = get_or_create_stats_for_user(user_id)
            return serialize_stats(stats), 200

        # /stats (lista todos)
        stats_list = UserStats.query.all()
        return [serialize_stats(s) for s in stats_list], 200

    def post(self):
        data = stats_parser.parse_args()

        # evitar duplicar stats do mesmo usuário
        existing = UserStats.query.filter_by(user_id=data["user_id"]).first()
        if existing:
            return {"message": "Stats já existe para esse usuário", "id": existing.id}, 409

        new_stats = UserStats(**data)
        db.session.add(new_stats)
        db.session.commit()
        return {"message": "Stats criado", "id": new_stats.id}, 201

    def put(self, stats_id):
        data = stats_parser.parse_args()
        stats = UserStats.query.get(stats_id)
        if not stats:
            return {"message": "Stats não encontrado"}, 404

        for key, value in data.items():
            setattr(stats, key, value)

        db.session.commit()
        return {"message": "Stats atualizado"}, 200

    def delete(self, stats_id):
        stats = UserStats.query.get(stats_id)
        if not stats:
            return {"message": "Stats não encontrado"}, 404

        db.session.delete(stats)
        db.session.commit()
        return {"message": "Stats deletado"}, 200


class MyStatsResource(Resource):
    """
    ✅ Endpoint real do usuário logado:
    GET /stats/me
    Usa o JWT para descobrir o user_id automaticamente.
    """
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        stats = get_or_create_stats_for_user(user_id)
        return serialize_stats(stats), 200
