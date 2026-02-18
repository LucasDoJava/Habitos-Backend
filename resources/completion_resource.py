from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from models.models import db, Habit, HabitCompletion, UserStats


completion_parser = reqparse.RequestParser()
completion_parser.add_argument("habit_id", type=int, required=True)
# Mantidos por compatibilidade, mas o backend NÃO confia neles:
completion_parser.add_argument("points_earned", type=int, required=False)
completion_parser.add_argument("notes", type=str, required=False)
completion_parser.add_argument("streak_day", type=int, required=False)


def update_achievements(stats: UserStats):
    if not stats.achievements:
        stats.achievements = {}

    ach = stats.achievements

    if stats.total_habits_completed >= 1:
        ach["first_completion"] = True
    if stats.total_habits_completed >= 10:
        ach["ten_completions"] = True
    if stats.total_habits_completed >= 20:
        ach["twenty_completions"] = True

    if stats.total_points >= 100:
        ach["points_100"] = True
    if stats.total_points >= 500:
        ach["points_500"] = True

    if stats.longest_streak >= 7:
        ach["streak_7"] = True
    if stats.longest_streak >= 30:
        ach["streak_30"] = True

    stats.achievements = ach


class CompletionResource(Resource):

    @jwt_required()
    def get(self, completion_id=None):
        user_id = int(get_jwt_identity())

        if completion_id:
            c = HabitCompletion.query.get(completion_id)
            if not c or c.user_id != user_id:
                return {"message": "Conclusão não encontrada"}, 404

            return {
                "id": c.id,
                "habit_id": c.habit_id,
                "points_earned": c.points_earned,
                "completed_at": c.completed_at.isoformat() if c.completed_at else None,
            }, 200

        completions = (
            HabitCompletion.query
            .filter_by(user_id=user_id)
            .order_by(HabitCompletion.completed_at.desc())
            .all()
        )

        return [
            {
                "id": c.id,
                "habit_id": c.habit_id,
                "points_earned": c.points_earned,
                "completed_at": c.completed_at.isoformat() if c.completed_at else None,
            }
            for c in completions
        ], 200

    @jwt_required()
    def post(self):
        user_id = int(get_jwt_identity())
        data = completion_parser.parse_args()

        habit_id = data.get("habit_id")
        notes = (data.get("notes") or "").strip()

        if habit_id is None:
            return {"message": "habit_id é obrigatório"}, 400

        # ✅ Hábito precisa existir e ser do usuário
        habit = Habit.query.filter_by(id=habit_id, user_id=user_id).first()
        if not habit:
            return {"message": "Hábito não encontrado"}, 404

        # 🔥 BLOQUEIO: só pode concluir 1x por dia
        already_completed_today = (
            db.session.query(HabitCompletion.id)
            .filter(HabitCompletion.user_id == user_id)
            .filter(HabitCompletion.habit_id == habit_id)
            .filter(func.date(HabitCompletion.completed_at) == func.curdate())
            .first()
        )

        if already_completed_today:
            return {"message": "Você já concluiu este hábito hoje."}, 400

        # ✅ Pontos SEMPRE vêm do banco
        points = int(habit.points or 0)

        # ✅ Garante stats
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
                total_habits_completed=0,
            )
            db.session.add(stats)

        # ✅ Registra completion
        new_completion = HabitCompletion(
            habit_id=habit_id,
            user_id=user_id,
            points_earned=points,
            notes=notes,
            streak_day=1,  # agora sempre 1 por dia
        )
        db.session.add(new_completion)

        # ✅ Atualiza total do hábito
        habit.total_completions = int(habit.total_completions or 0) + 1

        # Atualiza streak diária (agora sempre 1)
        habit.streak = 1
        habit.best_streak = max(int(habit.best_streak or 0), 1)

        # ✅ Atualiza stats do usuário
        stats.total_points = int(stats.total_points or 0) + points
        stats.current_exp = int(stats.current_exp or 0) + points
        stats.total_habits_completed = int(stats.total_habits_completed or 0) + 1

        # Conta total de conclusões do dia (todos hábitos)
        today_total_count = (
            db.session.query(func.count(HabitCompletion.id))
            .filter(HabitCompletion.user_id == user_id)
            .filter(func.date(HabitCompletion.completed_at) == func.curdate())
            .scalar()
        ) or 0

        stats.longest_streak = max(
            int(stats.longest_streak or 0),
            int(today_total_count)
        )

        # Level up
        while stats.current_exp >= stats.exp_to_next_level:
            stats.current_exp -= stats.exp_to_next_level
            stats.level += 1
            stats.exp_to_next_level += 50

        update_achievements(stats)

        db.session.commit()

        return {
            "message": "Conclusão registrada",
            "habit_id": habit_id,
            "points_added": points,
            "habit_today_streak": 1,
            "habit_record": int(habit.best_streak or 0),
            "today_total_completions": int(today_total_count),
        }, 201
