import json
from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Reserva, Movimiento, MovimientoSchema, TipoMovimiento, Banco, db
from datetime import datetime


class TestCrearMovimiento:

    def setup_method(self):
        self.usuario_1 = Usuario(usuario='usuario_1', contrasena='123456')
        self.usuario_2 = Usuario(usuario='usuario_2', contrasena='123456')
        db.session.add(self.usuario_1)
        db.session.add(self.usuario_2)
        db.session.commit()

        self.propiedad_1_usu_1 = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge Loaiza', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=self.usuario_1.id)
        self.propiedad_2_usu_1 = Propiedad(nombre_propiedad='Apto edificio Alto', ciudad='Bogota',
                              direccion='cra 100#7-21 apto 1302', nombre_propietario='Carlos Julio', numero_contacto='666777999', banco=Banco.NEQUI,
                              numero_cuenta='3122589635', id_usuario=self.usuario_1.id)
        db.session.add(self.propiedad_1_usu_1)
        db.session.add(self.propiedad_2_usu_1)
        db.session.commit()

        self.reserva_1 = Reserva(nombre='Julio Hernandez', fecha_ingreso=datetime.strptime('2023-01-03', '%Y-%m-%d'),
                          fecha_salida=datetime.strptime('2023-01-06', '%Y-%m-%d'), plataforma_reserva='Booking', total_reserva=568000,
                          comision='74800', id_propiedad=self.propiedad_1_usu_1.id)
        
        db.session.add(self.reserva_1)
        db.session.commit()

        self.datos_movimiento = {
            'concepto': 'Ingreso mascota',
            'tipo_movimiento': TipoMovimiento.INGRESO.value,
            'fecha': '2023-01-06T15:00:00',
            'valor': 123
        }

    def teardown_method(self):
        db.session.rollback()
        Propiedad.query.delete()
        Reserva.query.delete()
        Usuario.query.delete()
        Movimiento.query.delete()

    def actuar(self, client, id_propiedad, datos_movimiento=None, token=None):
        datos_movimiento = datos_movimiento or self.datos_movimiento
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.post(f'/propiedades/{id_propiedad}/movimientos', data=json.dumps(datos_movimiento), headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_retorna_201(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_1)
        assert self.respuesta.status_code == 201

    def test_retorna_movimiento_creado(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_1)
        assert self.respuesta_json
        assert 'id' in self.respuesta_json
        assert 'fecha' in self.respuesta_json
        assert 'valor' in self.respuesta_json
        assert 'concepto' in self.respuesta_json
        assert 'id_reserva' in self.respuesta_json
        assert 'id_propiedad' in self.respuesta_json

    def test_crea_registro_db(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_1)
        assert Movimiento.query.filter(Movimiento.id == self.respuesta_json['id'],
                                       Movimiento.id_propiedad == self.propiedad_1_usu_1.id).one_or_none()

    def test_retorna_401_token_no_enviado(self, client):
        self.datos_movimiento.update({'id_reserva': self.reserva_1.id})
        self.actuar(client, self.propiedad_1_usu_1.id)
        assert self.respuesta.status_code == 401

    def test_retorna_404_crear_movimiento_propiedad_otro_usuario(self, client):
        token_usuario_2 = create_access_token(identity=self.usuario_2.id)
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_2)
        assert self.respuesta.status_code == 404

    def test_crea_movimiento_propiedad_enviada_url(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.datos_movimiento.update({'id_propiedad': 123})
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_1)
        assert Movimiento.query.filter(Movimiento.id == self.respuesta_json['id'],
                                       Movimiento.id_propiedad == self.propiedad_1_usu_1.id).one_or_none()
