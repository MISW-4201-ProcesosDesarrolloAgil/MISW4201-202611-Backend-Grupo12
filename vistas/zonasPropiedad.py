from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError
from sqlalchemy import exc
from modelos import Zona, ZonaSchema, db
from vistas.utils import buscar_propiedad

zona_schema = ZonaSchema()

class VistaZonasPropiedad(Resource):

    @jwt_required()
    def post(self, id_propiedad):
        zona = Zona(
            nombre_zona=request.json.get("nombre_zona"),
            descripcion=request.json.get("descripcion"),
            id_propiedad=id_propiedad
        )
        db.session.add(zona)
        db.session.commit()

        return {}, 201