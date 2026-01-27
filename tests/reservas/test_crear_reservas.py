import json

from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Banco, Movimiento, TipoMovimiento, ReservaSchema, db
from modelos import Reserva


class TestCrearReservas:

    def setup_method(self):
        self.usuario_1 = Usuario(usuario='usuario_1', contrasena='123456')
        self.usuario_2 = Usuario(usuario='usuario_2', contrasena='123456')
        db.session.add(self.usuario_1)
        db.session.add(self.usuario_2)
        db.session.commit()

        self.propiedad_1_usu_1 = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge Loaiza', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=self.usuario_1.id)
        self.propiedad_1_usu_2 = Propiedad(nombre_propiedad='Apto edificio Alto', ciudad='Bogota',
                              direccion='cra 100#7-21 apto 1302', nombre_propietario='Carlos Julio', numero_contacto='666777999', banco=Banco.NEQUI,
                              numero_cuenta='3122589635', id_usuario=self.usuario_2.id)
        db.session.add(self.propiedad_1_usu_1)
        db.session.add(self.propiedad_1_usu_2)
        db.session.commit()

        self.datos_reserva = {
            'nombre': 'Pilar Pulido',
            'fecha_ingreso': '2023-01-06T15:00:00',
            'fecha_salida': '2023-01-08T12:00:00',
            'plataforma_reserva': 'Booking',
            'total_reserva': 586000,
            'comision': 74800,
            'numero_personas': 5,
            'observaciones': 'Necesitan parqueadero'
        }

    def teardown_method(self):
        db.session.rollback()
        Propiedad.query.delete()
        Reserva.query.delete()
        Usuario.query.delete()
        Movimiento.query.delete()

    def actuar(self, client, id_propiedad, datos_reserva=None, token=None):
        headers = {'Content-Type': 'application/json'}
        datos_reserva = datos_reserva or self.datos_reserva
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.post(f'/propiedades/{id_propiedad}/reservas', data=json.dumps(datos_reserva), headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_crear_reserva_propiedad_del_usuario_retorna_201(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, self.datos_reserva, token_usuario_1)
        self.respuesta.status_code == 201

    def test_crear_reserva_retorna_info_reserva_creada(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, self.datos_reserva, token_usuario_1)
        assert self.respuesta_json['nombre'] == 'Pilar Pulido'
        assert self.respuesta_json['fecha_ingreso'] == '2023-01-06T15:00:00'
        assert self.respuesta_json['fecha_salida'] == '2023-01-08T12:00:00'
        assert self.respuesta_json['plataforma_reserva'] == 'Booking'
        assert self.respuesta_json['total_reserva'] == 586000
        assert self.respuesta_json['comision'] == 74800
        assert self.respuesta_json['numero_personas'] == 5
        assert self.respuesta_json['observaciones'] == 'Necesitan parqueadero'

    def test_crear_reserva_propiedad_del_usuario_crea_registro_db(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, self.datos_reserva, token_usuario_1)
        reserva_db = Reserva.query.filter(Reserva.id_propiedad == self.propiedad_1_usu_1.id).all()
        assert len(reserva_db) == 1
    
    def test_crear_reserva_en_propiedad_de_otro_usuario_retorna_404(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, 123, self.datos_reserva, token_usuario_1)
        assert self.respuesta.status_code == 404
        assert self.respuesta_json == {'mensaje': 'propiedad no encontrada'}

    def test_reserva_se_crea_en_propiedad_enviada_en_url_no_en_propiedad_en_payload(self, client):
        token_usuario_2 = create_access_token(identity=self.usuario_2.id)
        self.datos_reserva.update({'id_propiedad': self.propiedad_1_usu_1.id})
        self.actuar(client, self.propiedad_1_usu_2.id, self.datos_reserva, token_usuario_2)

        assert Reserva.query.filter(Reserva.id_propiedad == self.propiedad_1_usu_2.id).one_or_none()

    def test_retorna_401_token_no_enviado(self, client):
        self.actuar(client, self.propiedad_1_usu_1.id, self.datos_reserva)
        assert self.respuesta.status_code == 401

    def test_crear_reserva_crea_movimiento_ingreso(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_1)
        reserva_id = self.respuesta_json['id']
        movimientos_ingreso = Movimiento.query.filter(Movimiento.id_propiedad == self.propiedad_1_usu_1.id,
                                                      Movimiento.id_reserva == reserva_id,
                                                      Movimiento.tipo_movimiento == TipoMovimiento.INGRESO).all()
        assert len(movimientos_ingreso) == 1
        movimiento_ingreso = movimientos_ingreso[0]
        assert movimiento_ingreso.valor == self.datos_reserva['total_reserva']
        assert movimiento_ingreso.concepto == Movimiento.CONCEPTO_RESERVA

    def test_crear_reserva_crea_movimiento_egreso(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, token=token_usuario_1)
        reserva_id = self.respuesta_json['id']
        movimientos_egreso = Movimiento.query.filter(Movimiento.id_propiedad == self.propiedad_1_usu_1.id,
                                                      Movimiento.id_reserva == reserva_id,
                                                      Movimiento.tipo_movimiento == TipoMovimiento.EGRESO).all()
        assert len(movimientos_egreso) == 1
        movimiento_egreso = movimientos_egreso[0]
        assert movimiento_egreso.valor == self.datos_reserva['comision']
        assert movimiento_egreso.concepto == Movimiento.CONCEPTO_COMISION
