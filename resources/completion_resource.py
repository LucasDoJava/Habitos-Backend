from flask_restful import Resource, reqparse
from models.models import db, HabitCompletion

completion_parser = reqparse.RequestParser()
completion_parser.add_argument("habit_id", type=int, required=True)
completion_parser.add_argument("user_id", type=int, required=True)
completion_parser.add_argument("points_earned", type=int, required=True)
completion_parser.add_argument("notes", type=str)
completion_parser.add_argument("streak_day", type=int)

class CompletionResource(Resource):
    def get(self, completion_id=None):
        if completion_id:
            c = HabitCompletion.query.get(completion_id)
            if not c:
                return {"message": "Conclusão não encontrada"}, 404
            return {
                "id": c.id,
                "habit_id": c.habit_id,
                "user_id": c.user_id,
                "points_earned": c.points_earned,
                "completed_at": c.completed_at.isoformat()
            }
        completions = HabitCompletion.query.all()
        return [ {"id": c.id, "habit_id": c.habit_id, "points": c.points_earned} for c in completions ]

    def post(self):
        data = completion_parser.parse_args()
        new_completion = HabitCompletion(**data)
        db.session.add(new_completion)
        db.session.commit()
        return {"message": "Conclusão registrada", "id": new_completion.id}, 201

    def delete(self, completion_id):
        c = HabitCompletion.query.get(completion_id)
        if not c:
            return {"message": "Conclusão não encontrada"}, 404
        db.session.delete(c)
        db.session.commit()
        return {"message": "Conclusão deletada"}
