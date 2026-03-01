from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError
from sqlalchemy import exc, select
from modelos import Zona, db, ElementoInventario, ElementoInventarioSchema, Propiedad
elemento_schema = ElementoInventarioSchema()

class VistaElementosInventario(Resource):

    def _verificar_acceso_zona(self, id_zona):
        zona = db.session.execute(
            select(Zona).filter(Zona.id == id_zona)
        ).scalar_one_or_none()

        if not zona:
            return None, ({'mensaje': 'Zona no encontrada'}, 404)

        propiedad = db.session.execute(
            select(Propiedad).filter(
                Propiedad.id == zona.id_propiedad,
                Propiedad.id_usuario == current_user.id
            )
        ).scalar_one_or_none()

        if not propiedad:
            return None, ({'mensaje': 'No tienes permiso'}, 403)

        return zona, None

    @jwt_required()
    def post(self, id_zona):
        zona, error = self._verificar_acceso_zona(id_zona)
        if error:
            return error
        try:
            elemento = elemento_schema.load(request.json, session=db.session)
            elemento.id_zona = id_zona
            db.session.add(elemento)
            db.session.commit()
        except ValidationError as validation_error:
            return validation_error.messages, 400
        except exc.IntegrityError:
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando el elemento. Revise los datos proporcionados'}, 400

        return elemento_schema.dump(elemento), 201

    @jwt_required()
    def get(self, id_zona):
        zona, error = self._verificar_acceso_zona(id_zona)
        if error:
            return error

        elementos = db.session.execute(
            select(ElementoInventario).filter(ElementoInventario.id_zona == id_zona)
        ).scalars().all()

        return elemento_schema.dump(elementos, many=True)
