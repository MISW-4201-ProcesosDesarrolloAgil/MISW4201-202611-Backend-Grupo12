from sqlalchemy import exc
from flask import request
from flask_jwt_extended import create_access_token, current_user, jwt_required
from flask_restful import Resource

from modelos import db, Usuario, UsuarioSchema

usuario_schema = UsuarioSchema()


class VistaSignIn(Resource):

    def post(self):
        nuevo_usuario = Usuario(usuario=request.json["usuario"], contrasena=request.json["contrasena"])
        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
        except exc.IntegrityError:
            db.session.rollback()
            return {"mensaje": "Ya existe un usuario con este identificador"}, 400
        token_de_acceso = create_access_token(identity=str(nuevo_usuario.id))
        return {"mensaje": "usuario creado", "token": token_de_acceso, "id": nuevo_usuario.id}, 201

    @jwt_required()
    def put(self, id_usuario):
        usuario_token = current_user
        if id_usuario != current_user.id:
            return {"mensaje": "Peticion invalida"}, 400
        usuario_token.contrasena = request.json.get("contrasena", usuario_token.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario_token)
