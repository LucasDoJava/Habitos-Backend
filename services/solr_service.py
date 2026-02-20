import requests
from datetime import datetime

SOLR_URL = "http://solr:8983/solr"

def solr_commit(core):
    requests.get(f"{SOLR_URL}/{core}/update?commit=true")

def index_user(user):
    doc = {
        "id": f"user_{user.id}",
        "user_id_i": user.id,
        "name_t": user.name,
        "email_t": user.email,
        "avatar_s": user.avatar,
        "created_at_dt": user.created_at.isoformat() + "Z"
    }

    requests.post(
        f"{SOLR_URL}/users/update",
        json=[doc]
    )

    solr_commit("users")


def index_habit(habit):
    doc = {
        "id": f"habit_{habit.id}",
        "habit_id_i": habit.id,
        "user_id_i": habit.user_id,
        "name_t": habit.name,
        "description_t": habit.description or "",
        "category_s": habit.category,
        "difficulty_s": habit.difficulty,
        "is_active_b": habit.is_active,
        "created_at_dt": habit.created_at.isoformat() + "Z"
    }

    requests.post(
        f"{SOLR_URL}/habits/update",
        json=[doc]
    )

    solr_commit("habits")


def delete_document(core, doc_id):
    requests.post(
        f"{SOLR_URL}/{core}/update",
        json={"delete": {"id": doc_id}}
    )
    solr_commit(core)
