import json
from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Reserva, Banco, db
from datetime import datetime

class TestActualizarReserva:

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

        self.nuevos_datos_reserva = {
            'nombre': 'nuevo nombre',
            'fecha_ingreso': '2023-01-07T15:00:00',
            'fecha_salida': '2023-01-09T12:00:00'
        }

    def teardown_method(self):
        db.session.rollback()
        Propiedad.query.delete()
        Reserva.query.delete()
        Usuario.query.delete()

    def actuar(self, client, id_reserva, datos_reserva=None, token=None):
        headers = {'Content-Type': 'application/json'}
        datos_reserva = datos_reserva or self.nuevos_datos_reserva
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.put(f'/reservas/{id_reserva}', data=json.dumps(datos_reserva), headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_retorna_200_al_actualizar_reserva(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id) 
        self.actuar(client, id_reserva=self.reserva_1.id, token=token_usuario_1)
        assert self.respuesta.status_code == 200

    def test_retorna_401_no_token(self, client):
        self.actuar(client, id_reserva=self.reserva_1.id)
        assert self.respuesta.status_code == 401

    def test_actualiza_solo_campos_enviados(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id) 
        self.actuar(client, id_reserva=self.reserva_1.id, token=token_usuario_1)

        reserva_db = Reserva.query.filter(Reserva.id == self.reserva_1.id).first()
        assert reserva_db.nombre == 'nuevo nombre'
        assert str(reserva_db.fecha_ingreso) == '2023-01-07 15:00:00'
        assert str(reserva_db.fecha_salida) == '2023-01-09 12:00:00'
        assert reserva_db.comision == 74800
        assert reserva_db.plataforma_reserva == 'Booking'
        assert reserva_db.total_reserva == 568000
        assert reserva_db.id_propiedad == self.propiedad_1_usu_1.id

    def test_retorna_404_si_reserva_no_es_de_propiedad_del_usuario(self, client):
        token_usuario_2 = create_access_token(identity=self.usuario_2.id) 
        self.actuar(client, id_reserva=self.reserva_1.id, token=token_usuario_2)
        assert self.respuesta.status_code == 404
        assert self.respuesta_json == {"mensaje": "reserva no encontrada"}
