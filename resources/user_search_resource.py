from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flask import request
import requests


class UserSearchResource(Resource):

    @jwt_required()
    def get(self):
        query = request.args.get("q", "").strip()
        autocomplete = request.args.get("autocomplete", "false").lower() == "true"

        if not query:
            return {"users": []}, 200

        solr_query = f"name_t:{query}* OR email_t:{query}*" if autocomplete else query
        rows = 5 if autocomplete else 20
        fl = "user_id,name_t,email_t"

        try:
            response = requests.get(
                "http://localhost:8983/solr/users/select",  # ← ajuste se estiver no docker
                params={
                    "q": solr_query,
                    "fl": fl,
                    "rows": rows,
                    "wt": "json"
                },
                timeout=5
            )
            response.raise_for_status()
        except requests.RequestException as e:
            return {"message": f"Erro ao consultar Solr: {str(e)}"}, 500

        data = response.json()
        docs = data.get("response", {}).get("docs", [])

        # 🔥 CONVERSÃO AQUI
        users = [
            {
                "id": doc.get("user_id"),
                "name": doc.get("name_t"),
                "email": doc.get("email_t"),
            }
            for doc in docs
        ]

        return {"users": users}, 200
