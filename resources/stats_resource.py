from flask_restful import Resource, reqparse
from models.models import db, UserStats

stats_parser = reqparse.RequestParser()
stats_parser.add_argument("user_id", type=int, required=True)
stats_parser.add_argument("level", type=int)
stats_parser.add_argument("total_points", type=int)
stats_parser.add_argument("current_exp", type=int)
stats_parser.add_argument("exp_to_next_level", type=int)
stats_parser.add_argument("achievements", type=dict)
stats_parser.add_argument("longest_streak", type=int)
stats_parser.add_argument("total_habits_completed", type=int)

class StatsResource(Resource):
    def get(self, stats_id=None):
        if stats_id:
            stats = UserStats.query.get(stats_id)
            if not stats:
                return {"message": "Stats não encontrado"}, 404
            return {
                "id": stats.id,
                "user_id": stats.user_id,
                "level": stats.level,
                "total_points": stats.total_points
            }
        stats = UserStats.query.all()
        return [ {"id": s.id, "user_id": s.user_id, "level": s.level} for s in stats ]

    def post(self):
        data = stats_parser.parse_args()
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
        return {"message": "Stats atualizado"}

    def delete(self, stats_id):
        stats = UserStats.query.get(stats_id)
        if not stats:
            return {"message": "Stats não encontrado"}, 404
        db.session.delete(stats)
        db.session.commit()
        return {"message": "Stats deletado"}
