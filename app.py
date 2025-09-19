from flask import Flask
from flask_restful import Api
from resources.user_resource import UserResource
from resources.habit_resource import HabitResource
from resources.completion_resource import CompletionResource
from resources.stats_resource import StatsResource

from helpers.application import app, api
from helpers.database import db
from resources.user_resource import UserResource


api.add_resource(UserResource, "/users", "/users/<int:user_id>")
api.add_resource(HabitResource, "/habits", "/habits/<int:habit_id>")
api.add_resource(CompletionResource, "/completions", "/completions/<int:completion_id>")
api.add_resource(StatsResource, "/stats", "/stats/<int:stats_id>")

if __name__ == "__main__":
    app.run(debug=True)