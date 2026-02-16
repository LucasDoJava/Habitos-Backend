from sqlalchemy import func, desc
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models.models import db, User, UserStats

class RankingResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())

        rows = (
            db.session.query(
                User,
                UserStats
            )
            .outerjoin(UserStats, UserStats.user_id == User.id)  # ✅ OUTER JOIN
            .order_by(
                func.coalesce(UserStats.total_points, 0).desc(),
                func.coalesce(UserStats.level, 1).desc(),
                func.coalesce(UserStats.total_habits_completed, 0).desc()
            )
            .all()
        )

        ranking = []
        my_rank = None

        for idx, (u, s) in enumerate(rows, start=1):

            total_points = s.total_points if s else 0
            level = s.level if s else 1
            total_completed = s.total_habits_completed if s else 0
            longest_streak = s.longest_streak if s else 0

            item = {
                "rank": idx,
                "user_id": u.id,
                "name": u.name,
                "avatar": getattr(u, "avatar", None),
                "level": level,
                "total_points": total_points,
                "total_habits_completed": total_completed,
                "longest_streak": longest_streak,
            }

            ranking.append(item)

            if u.id == user_id:
                my_rank = item

        return {
            "ranking": ranking,
            "me": my_rank
        }, 200
