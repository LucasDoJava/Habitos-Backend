from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, or_
from models.models import db, User, UserStats, FriendRequest


class RankingResource(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())

        # 🔥 Buscar amizades aceitas envolvendo o usuário
        friendships = (
            db.session.query(FriendRequest)
            .filter(
                FriendRequest.status == "accepted",
                or_(
                    FriendRequest.sender_id == user_id,
                    FriendRequest.receiver_id == user_id
                )
            )
            .all()
        )

        # 🔥 Extrair IDs dos amigos
        friend_ids = []

        for friendship in friendships:
            if friendship.sender_id == user_id:
                friend_ids.append(friendship.receiver_id)
            else:
                friend_ids.append(friendship.sender_id)

        # 🔥 Incluir o próprio usuário
        friend_ids.append(user_id)

        # 🔥 Buscar ranking apenas entre amigos + eu
        rows = (
            db.session.query(User, UserStats)
            .outerjoin(UserStats, UserStats.user_id == User.id)
            .filter(User.id.in_(friend_ids))
            .order_by(
                func.coalesce(UserStats.total_points, 0).desc(),
                func.coalesce(UserStats.level, 1).desc(),
                func.coalesce(UserStats.total_habits_completed, 0).desc()
            )
            .all()
        )

        ranking = []
        my_rank = None

        for position, (user, stats) in enumerate(rows, start=1):
            total_points = stats.total_points if stats else 0
            level = stats.level if stats else 1
            total_completed = stats.total_habits_completed if stats else 0
            longest_streak = stats.longest_streak if stats else 0

            item = {
                "rank": position,
                "user_id": user.id,
                "name": user.name,
                "avatar": getattr(user, "avatar", None),
                "level": level,
                "total_points": total_points,
                "total_habits_completed": total_completed,
                "longest_streak": longest_streak,
            }

            ranking.append(item)

            if user.id == user_id:
                my_rank = item

        return {
            "ranking": ranking,
            "me": my_rank
        }, 200
