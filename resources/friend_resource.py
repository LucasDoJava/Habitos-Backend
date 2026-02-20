from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.models import User, db, FriendRequest


friend_request_parser = reqparse.RequestParser()
friend_request_parser.add_argument("receiver_id", type=int, required=True, location="json")


class FriendRequestResource(Resource):
     
       @jwt_required()
       def post(self):
        sender_id = int(get_jwt_identity())
        data = friend_request_parser.parse_args()
        receiver_id = data["receiver_id"]

        if sender_id == receiver_id:
            return {"message": "Você não pode enviar pedido para si mesmo."}, 400

        receiver = User.query.get(receiver_id)
        if not receiver:
            return {"message": "Usuário não encontrado."}, 404

        existing = FriendRequest.query.filter(
            ((FriendRequest.sender_id == sender_id) & (FriendRequest.receiver_id == receiver_id)) |
            ((FriendRequest.sender_id == receiver_id) & (FriendRequest.receiver_id == sender_id))
        ).first()

        if existing:
            if existing.status == "pending":
                return {"message": "Pedido já enviado ou pendente."}, 400
            if existing.status == "accepted":
                return {"message": "Vocês já são amigos."}, 400

        new_request = FriendRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            status="pending"
        )
        db.session.add(new_request)
        db.session.commit()

        return {"message": "Pedido de amizade enviado com sucesso."}, 201


class PendingFriendRequestsResource(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())

        requests = FriendRequest.query.filter_by(
            receiver_id=user_id,
            status="pending"
        ).all()

        return [
            {
                "id": r.id,
                "sender_id": r.sender.id,
                "sender_name": r.sender.name,
                "sender_email": r.sender.email,
            }
            for r in requests
        ], 200


class RespondFriendRequestResource(Resource):

    @jwt_required()
    def put(self, request_id, action):
        user_id = int(get_jwt_identity())

        request = FriendRequest.query.get(request_id)

        if not request:
            return {"message": "Pedido não encontrado."}, 404

        if request.receiver_id != user_id:
            return {"message": "Ação não permitida."}, 403

        if request.status != "pending":
            return {"message": "Pedido já respondido."}, 400

        if action == "accept":
            request.status = "accepted"
        elif action == "reject":
            request.status = "rejected"
        else:
            return {"message": "Ação inválida."}, 400

        db.session.commit()

        return {"message": f"Pedido {action}ado com sucesso."}, 200


class FriendsListResource(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())

        friends = FriendRequest.query.filter(
            ((FriendRequest.sender_id == user_id) |
             (FriendRequest.receiver_id == user_id)) &
            (FriendRequest.status == "accepted")
        ).all()

        result = []

        for f in friends:
            friend_user = (
                f.receiver if f.sender_id == user_id else f.sender
            )

            result.append({
                "id": friend_user.id,
                "name": friend_user.name,
                "email": friend_user.email,
            })

        return result, 200
