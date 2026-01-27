from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from sqlalchemy import delete
from modelos import Propiedad, PropiedadSchema, db
from vistas.utils import buscar_propiedad

propiedad_schema = PropiedadSchema()

class VistaPropiedad(Resource):

    @jwt_required()
    def put(self, id_propiedad):
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
            return resultado_buscar_propiedad.error
        for key, value in request.json.items():
            setattr(resultado_buscar_propiedad.propiedad, key, value)
        db.session.commit() 
        return propiedad_schema.dump(resultado_buscar_propiedad.propiedad)
    
    @jwt_required()
    def delete(self, id_propiedad):
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
            return resultado_buscar_propiedad.error
        db.session.execute(delete(Propiedad).filter(Propiedad.id == id_propiedad))
        db.session.commit()
        return "", 204
    
    @jwt_required()
    def get(self, id_propiedad):
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
            return resultado_buscar_propiedad.error
        return propiedad_schema.dump(resultado_buscar_propiedad.propiedad)
