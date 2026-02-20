from flask import Flask
from flask_restful import Api
from resources.user_resource import UserResource
from resources.habit_resource import HabitResource
from resources.completion_resource import CompletionResource
from resources.stats_resource import StatsResource, MyStatsResource
from resources.login_resource import LoginResource
from resources.ranking_resource import RankingResource
from resources.friend_resource import FriendRequestResource, FriendsListResource, PendingFriendRequestsResource, RespondFriendRequestResource
from resources.habit_search_resource import HabitSearchResource

from helpers.application import app, api
from helpers.database import db
from resources.user_resource import UserResource
from resources.user_search_resource import UserSearchResource

api.add_resource(UserResource, "/users", "/users/<int:user_id>")
api.add_resource(HabitResource, "/habits", "/habits/<int:habit_id>")
api.add_resource(CompletionResource, "/completions", "/completions/<int:completion_id>")
api.add_resource(StatsResource, "/stats", "/stats/<int:stats_id>")
api.add_resource(MyStatsResource, "/stats/me")
api.add_resource(LoginResource, "/login")
api.add_resource(RankingResource, "/ranking")
api.add_resource(FriendRequestResource, "/friend-request")
api.add_resource(PendingFriendRequestsResource, "/friend-request/pending")
api.add_resource(RespondFriendRequestResource, "/friend-request/<int:request_id>/<string:action>")
api.add_resource(FriendsListResource, "/friends")

api.add_resource(HabitSearchResource, "/habits/search")
api.add_resource(UserSearchResource, "/users/search")


if __name__ == "__main__":
    app.run(debug=True)