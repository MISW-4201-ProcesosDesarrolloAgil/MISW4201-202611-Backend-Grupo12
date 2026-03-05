from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from sqlalchemy import select
from vistas.bancos import VistaBancos
from vistas.movimiento import VistaMovimiento
from vistas.movimientos import VistaMovimientos
from vistas.ingresos import VistaIngresos
from vistas.egresos import VistaEgresos
from vistas.propiedades import VistaPropiedades
from vistas.propiedad import VistaPropiedad
from vistas.reserva import VistaReserva
from vistas.reservas import VistaReservas
from vistas.sign_in import VistaSignIn
from vistas.login import VistaLogIn
from modelos import db, Usuario
from vistas.tipo_movimientos import VistaTipoMovimientos


app = None


def create_flask_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///admon_reservas.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "frase-secreta"
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["JWT_IDENTITY_CLAIM"] = "sub"

    app_context = app.app_context()
    app_context.push()
    add_urls(app)
    CORS(
        app,
        origins="*",
    )

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.execute(
            select(Usuario).filter_by(id=int(identity))
        ).scalar_one_or_none()

    return app


def add_urls(app):
    api = Api(app)
    api.add_resource(VistaSignIn, "/signin", "/signin/<int:id_usuario>")
    api.add_resource(VistaLogIn, "/login")
    api.add_resource(VistaPropiedades, "/propiedades")
    api.add_resource(VistaPropiedad, "/propiedades/<int:id_propiedad>")
    api.add_resource(VistaReservas, "/propiedades/<int:id_propiedad>/reservas")
    api.add_resource(VistaReserva, "/reservas/<int:id_reserva>")
    api.add_resource(VistaMovimientos, "/propiedades/<int:id_propiedad>/movimientos")
    api.add_resource(VistaMovimiento, "/movimientos/<int:id_movimiento>")
    api.add_resource(VistaIngresos, "/propiedades/<int:id_propiedad>/ingresos")
    api.add_resource(VistaEgresos, "/propiedades/<int:id_propiedad>/egresos")
    api.add_resource(VistaBancos, "/bancos")
    api.add_resource(VistaTipoMovimientos, "/tipo-movimientos")


app = create_flask_app()
db.init_app(app)
db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
