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
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
            return resultado_buscar_propiedad.error
        zona = zona_schema.load(request.json, session=db.session)
        zona.id_propiedad = id_propiedad
        db.session.add(zona)
        db.session.commit()

        return zona_schema.dump(zona), 201