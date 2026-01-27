from datetime import datetime

from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Reserva, ReservaSchema, Banco, db

class TestObtenerReserva:

    def setup_method(self):
        self.usuario_1 = Usuario(usuario='usuario_1', contrasena='123456')
        self.usuario_2 = Usuario(usuario='usuario_2', contrasena='123456')
        db.session.add(self.usuario_1)
        db.session.add(self.usuario_2)
        db.session.commit()

        self.propiedad_1_usu_1 = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge Loaiza', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=self.usuario_1.id)
        db.session.add(self.propiedad_1_usu_1)
        db.session.commit()

        self.reserva_1 = Reserva(nombre='Julio Hernandez', fecha_ingreso=datetime.strptime('2023-01-03', '%Y-%m-%d'),
                          fecha_salida=datetime.strptime('2023-01-06', '%Y-%m-%d'), plataforma_reserva='Booking', total_reserva=568000,
                          comision='74800', id_propiedad=self.propiedad_1_usu_1.id)
        db.session.add(self.reserva_1)
        db.session.commit()

    def teardown_method(self):
        db.session.rollback()
        Propiedad.query.delete()
        Reserva.query.delete()
        Usuario.query.delete()

    def actuar(self, client, id_reserva, token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.get(f'/reservas/{id_reserva}', headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_retorna_200_si_reserva_existe_y_es_de_propiedad_usuario(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.reserva_1.id, token=token_usuario_1)
        assert self.respuesta.status_code == 200

    def test_retorna_info_reserva(self, client):
        reserva_schema = ReservaSchema()
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.reserva_1.id, token=token_usuario_1)
        assert self.respuesta_json == reserva_schema.dump(self.reserva_1)

    def test_retorna_404_si_reserva_no_existe(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, 123, token=token_usuario_1)
        assert self.respuesta.status_code == 404

    def test_retorna_404_si_reserva_no_es_de_propiedad_usuario(self, client):
        token_usuario_2 = create_access_token(identity=self.usuario_2.id)
        self.actuar(client, self.reserva_1.id, token=token_usuario_2)
        assert self.respuesta.status_code == 404

    def test_retorna_401_token_no_enviado(self, client):
        self.actuar(client, 123)
        assert self.respuesta.status_code == 401
