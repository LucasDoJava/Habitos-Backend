from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from helpers.database import db

from werkzeug.security import generate_password_hash, check_password_hash



class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    habits = db.relationship("Habit", backref="user", cascade="all, delete-orphan")
    completions = db.relationship("HabitCompletion", backref="user", cascade="all, delete-orphan")
    stats = db.relationship("UserStats", uselist=False, backref="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Habit(db.Model):
    __tablename__ = "habits"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.Enum("saude", "produtividade", "exercicio", "estudo", "social", "outro", name="habit_category"), nullable=False)
    difficulty = db.Column(db.Enum("facil", "medio", "dificil", name="habit_difficulty"), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    streak = db.Column(db.Integer, default=0)
    best_streak = db.Column(db.Integer, default=0)
    total_completions = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    icon = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    completions = db.relationship("HabitCompletion", backref="habit", cascade="all, delete-orphan")


class HabitCompletion(db.Model):
    __tablename__ = "habit_completions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    habit_id = db.Column(db.Integer, db.ForeignKey("habits.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    points_earned = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    streak_day = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserStats(db.Model):
    __tablename__ = "user_stats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    level = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)
    current_exp = db.Column(db.Integer, default=0)
    exp_to_next_level = db.Column(db.Integer, default=100)
    achievements = db.Column(db.JSON, default=[])
    longest_streak = db.Column(db.Integer, default=0)
    total_habits_completed = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
