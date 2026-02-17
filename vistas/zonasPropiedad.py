from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, current_user
from modelos import Zona, ZonaSchema, db
from vistas.utils import buscar_propiedad

zona_schema = ZonaSchema()

class VistaZonasPropiedad(Resource):

    @jwt_required()
    def post(self, id_propiedad):
        return
