from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, current_user
from marshmallow import ValidationError
from sqlalchemy import exc, select
from modelos import Zona, db, ElementoInventario, ElementoInventarioSchema, Propiedad
elemento_schema = ElementoInventarioSchema()
class VistaElementosInventario(Resource):
    @jwt_required()
    def post(self, id_zona):
        try:
            # 1. Verificar que la zona existe PRIMERO
            zona = db.session.execute(
                select(Zona).filter(Zona.id == id_zona)
            ).scalar_one_or_none()
            
            if not zona:
                return {'mensaje': 'Zona no encontrada'}, 404
            
            # 2. Verificar que la propiedad pertenece al usuario
            propiedad = db.session.execute(
                select(Propiedad).filter(
                    Propiedad.id == zona.id_propiedad,
                    Propiedad.id_usuario == current_user.id
                )
            ).scalar_one_or_none()
            
            if not propiedad:
                return {'mensaje': 'No tienes permiso'}, 403
            
            # 3. Cargar datos del elemento desde el request
            elemento = elemento_schema.load(request.json, session=db.session)
            elemento.id_zona = id_zona
            
            # 4. Guardar en BD
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
        """
        Obtener todos los elementos de inventario de una zona.
        Solo el propietario puede verlos.
        """
        # Verificar que la zona existe
        zona = db.session.execute(
            select(Zona).filter(Zona.id == id_zona)
        ).scalar_one_or_none()
        
        if not zona:
            return {'mensaje': 'Zona no encontrada'}, 404
        
        # Verificar que la propiedad pertenece al usuario actual
        propiedad = db.session.execute(
            select(Propiedad).filter(
                Propiedad.id == zona.id_propiedad,
                Propiedad.id_usuario == current_user.id
            )
        ).scalar_one_or_none()
        
        if not propiedad:
            return {'mensaje': 'No tienes permiso para ver elementos en esta zona'}, 403
        
        elementos = db.session.execute(
            select(ElementoInventario).filter(ElementoInventario.id_zona == id_zona)
        ).scalars().all()
        
        return elemento_schema.dump(elementos, many=True)
