from flask import jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from modelos import ZonaPosible

class VistaZonasPosibles(Resource):
    
    @jwt_required()
    def get(self):
        return jsonify([zona.name for zona in ZonaPosible])