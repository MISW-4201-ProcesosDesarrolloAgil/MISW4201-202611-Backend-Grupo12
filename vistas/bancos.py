from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from modelos import Banco


class VistaBancos(Resource):

    @jwt_required()
    def get(self):
        return jsonify([banco.name for banco in Banco])
