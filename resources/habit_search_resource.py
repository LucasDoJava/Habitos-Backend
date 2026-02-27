from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
import requests

class HabitSearchResource(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        query = request.args.get("q", "*")
        autocomplete = request.args.get("autocomplete", "false").lower() == "true" #autocomplete

        # usa prefix query
        if autocomplete and query != "*":
            solr_query = f"name_t:{query}*"
            rows = 5
            fl = "name_t"
        else:
            # Busca normal 
            solr_query = query
            rows = 20
            fl = "*"

        response = requests.get(
            "http://solr:8983/solr/habits/select",
            params={
                "q": solr_query,
                "fq": f"user_id_i:{user_id}",
                "fl": fl,
                "rows": rows,
                "wt": "json"
            }
        )

        data = response.json()

        if autocomplete:
            suggestions = [doc["name_t"] for doc in data["response"]["docs"]]
            return {"suggestions": suggestions}, 200 #retornar nomes semelhantes

        return data, 200
