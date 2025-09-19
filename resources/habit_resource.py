from flask_restful import Resource, reqparse
from models.models import db, Habit

habit_parser = reqparse.RequestParser()
habit_parser.add_argument("user_id", type=int, required=True, help="Usuário é obrigatório")
habit_parser.add_argument("name", type=str, required=True)
habit_parser.add_argument("description", type=str)
habit_parser.add_argument("category", type=str, required=True)
habit_parser.add_argument("difficulty", type=str, required=True)
habit_parser.add_argument("points", type=int, required=True)
habit_parser.add_argument("icon", type=str)
habit_parser.add_argument("color", type=str)

class HabitResource(Resource):
    def get(self, habit_id=None):
        if habit_id:
            habit = Habit.query.get(habit_id)
            if not habit:
                return {"message": "Hábito não encontrado"}, 404
            return {
                "id": habit.id,
                "name": habit.name,
                "description": habit.description,
                "points": habit.points,
                "streak": habit.streak
            }
        habits = Habit.query.all()
        return [ {"id": h.id, "name": h.name, "points": h.points} for h in habits ]

    def post(self):
        data = habit_parser.parse_args()
        new_habit = Habit(**data)
        db.session.add(new_habit)
        db.session.commit()
        return {"message": "Hábito criado", "id": new_habit.id}, 201

    def put(self, habit_id):
        data = habit_parser.parse_args()
        habit = Habit.query.get(habit_id)
        if not habit:
            return {"message": "Hábito não encontrado"}, 404
        for key, value in data.items():
            setattr(habit, key, value)
        db.session.commit()
        return {"message": "Hábito atualizado"}

    def delete(self, habit_id):
        habit = Habit.query.get(habit_id)
        if not habit:
            return {"message": "Hábito não encontrado"}, 404
        db.session.delete(habit)
        db.session.commit()
        return {"message": "Hábito deletado"}
