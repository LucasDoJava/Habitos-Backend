from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models.models import db, Habit, HabitCompletion
from services.solr_service import index_habit
from services.solr_service import delete_document



habit_parser = reqparse.RequestParser()
habit_parser.add_argument("name", type=str, required=True, help="Nome é obrigatório")
habit_parser.add_argument("description", type=str, required=False)
habit_parser.add_argument("category", type=str, required=True, help="Categoria é obrigatória")
habit_parser.add_argument("difficulty", type=str, required=False)
habit_parser.add_argument("points", type=int, required=False)
habit_parser.add_argument("icon", type=str, required=False)
habit_parser.add_argument("color", type=str, required=False)
habit_parser.add_argument("isActive", type=bool, required=False)


def serialize_habit(h: Habit):
    return {
        "id": h.id,
        "user_id": h.user_id,
        "name": h.name,
        "description": h.description,
        "category": h.category,
        "difficulty": h.difficulty,
        "points": h.points,
        "streak": h.streak,
        "bestStreak": h.best_streak,
        "totalCompletions": h.total_completions,
        "isActive": h.is_active,
        "icon": h.icon,
        "color": h.color,
        "createdAt": h.created_at.isoformat() if h.created_at else None,
    }


class HabitResource(Resource):
    @jwt_required()
    def get(self, habit_id=None):
        user_id = int(get_jwt_identity())

        # ✅ Se pedir um hábito específico
        if habit_id is not None:
            habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
            if not habit:
                return {"message": "Hábito não encontrado"}, 404

            payload = serialize_habit(habit)

            # ✅ streak sempre representa "hoje" (zera automaticamente quando vira o dia)
            today_count = (
                db.session.query(func.count(HabitCompletion.id))
                .filter(HabitCompletion.user_id == user_id)
                .filter(HabitCompletion.habit_id == habit.id)
                .filter(func.date(HabitCompletion.completed_at) == func.curdate())
                .scalar()
            ) or 0

            payload["streak"] = int(today_count)
            return payload, 200

        # ✅ Lista hábitos do usuário
        habits = Habit.query.filter_by(user_id=user_id).all()
        habit_ids = [h.id for h in habits]

        # mapa: habit_id -> contagem de conclusões HOJE
        today_map = {}
        if habit_ids:
            rows = (
                db.session.query(HabitCompletion.habit_id, func.count(HabitCompletion.id))
                .filter(HabitCompletion.user_id == user_id)
                .filter(HabitCompletion.habit_id.in_(habit_ids))
                .filter(func.date(HabitCompletion.completed_at) == func.curdate())
                .group_by(HabitCompletion.habit_id)
                .all()
            )
            today_map = {hid: int(cnt) for hid, cnt in rows}

        result = []
        for h in habits:
            payload = serialize_habit(h)
            payload["streak"] = today_map.get(h.id, 0)  # ✅ sequência do dia
            result.append(payload)

        return result, 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        data = habit_parser.parse_args()

        difficulty = data.get("difficulty") or "facil"
        points = data.get("points") if data.get("points") is not None else 10
        icon = data.get("icon") or "🎯"
        color = data.get("color") or "#7c3aed"

        habit = Habit(
            user_id=user_id,
            name=data["name"],
            description=data.get("description"),
            category=data["category"],
            difficulty=difficulty,
            points=int(points),
            icon=icon,
            color=color,
            is_active=True if data.get("isActive") is None else bool(data.get("isActive")),
        )

        db.session.add(habit)
        db.session.commit()
        index_habit(habit)


        return serialize_habit(habit), 201

    @jwt_required()
    def put(self, habit_id):
        user_id = int(get_jwt_identity())
        data = habit_parser.parse_args()

        habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
        if not habit:
            return {"message": "Hábito não encontrado"}, 404

        if data.get("name") is not None:
            habit.name = data["name"]
        if data.get("description") is not None:
            habit.description = data["description"]
        if data.get("category") is not None:
            habit.category = data["category"]
        if data.get("difficulty") is not None:
            habit.difficulty = data["difficulty"]
        if data.get("points") is not None:
            habit.points = int(data["points"])
        if data.get("icon") is not None:
            habit.icon = data["icon"]
        if data.get("color") is not None:
            habit.color = data["color"]
        if data.get("isActive") is not None:
            habit.is_active = bool(data["isActive"])

        db.session.commit()
        return serialize_habit(habit), 200

    @jwt_required()
    def delete(self, habit_id):
        user_id = int(get_jwt_identity())

        habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
        if not habit:
            return {"message": "Hábito não encontrado"}, 404

        habit_solr_id = f"habit_{habit.id}"

        db.session.delete(habit)
        db.session.commit()

        delete_document("habits", habit_solr_id)

        return {"message": "Hábito deletado"}, 200
