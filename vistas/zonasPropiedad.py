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
        try:
            zona = zona_schema.load(request.json, session=db.session)
            zona.id_propiedad = id_propiedad
            db.session.add(zona)
            db.session.commit()
        except ValidationError as validation_error:
            return validation_error.messages, 400
        except exc.IntegrityError:
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando la zona. Revise los datos proporcionados'}, 400
        return zona_schema.dump(zona), 201