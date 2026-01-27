from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from sqlalchemy import select
from modelos import Usuario, db


class VistaLogIn(Resource):

    def post(self):
        usuario = db.session.execute(
            select(Usuario).filter(
                Usuario.usuario == request.json["usuario"],
                Usuario.contrasena == request.json["contrasena"]
            )
        ).scalar_one_or_none()
        if usuario is None:
            return "Verifique los datos ingresados", 404
        token_de_acceso = create_access_token(identity=str(usuario.id))
        return {"mensaje": "Inicio de sesion exitoso", "token": token_de_acceso}
