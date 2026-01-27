from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import exc, select

from modelos import Propiedad, db, PropiedadSchema

propiedad_schema = PropiedadSchema()


class VistaPropiedades(Resource):

    @jwt_required()
    def post(self):
        try:
            propiedad = propiedad_schema.load(request.json, session=db.session)
            propiedad.id_usuario = current_user.id
            db.session.add(propiedad)
            db.session.commit()
        except ValidationError as validation_error:
            return validation_error.messages, 400
        except exc.IntegrityError as e:
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando la propiedad. Revise los datos proporcionados'}, 400
        return propiedad_schema.dump(propiedad), 201
    
    @jwt_required()
    def get(self):
        propiedades = db.session.execute(
            select(Propiedad).filter(Propiedad.id_usuario == current_user.id)
        ).scalars().all()
        return propiedad_schema.dump(propiedades, many=True)
