from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Reserva, Movimiento, MovimientoSchema, TipoMovimiento, Banco, db
from datetime import datetime


class TestObtenerMovimiento:

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

        self.movimiento_reserva = Movimiento(fecha=datetime.strptime('2023-01-06', '%Y-%m-%d'), valor=12345.25,
                                     concepto=Movimiento.CONCEPTO_RESERVA, tipo_movimiento=TipoMovimiento.INGRESO,
                                     id_propiedad=self.propiedad_1_usu_1.id, id_reserva=self.reserva_1.id)
        self.movimiento_comision = Movimiento(fecha=datetime.strptime('2023-01-06', '%Y-%m-%d'), valor=11.56,
                                     concepto=Movimiento.CONCEPTO_COMISION, tipo_movimiento=TipoMovimiento.INGRESO,
                                     id_propiedad=self.propiedad_1_usu_1.id, id_reserva=self.reserva_1.id)
        db.session.add(self.movimiento_reserva)
        db.session.add(self.movimiento_comision)
        db.session.commit()

    def teardown_method(self):
        db.session.rollback()
        Propiedad.query.delete()
        Reserva.query.delete()
        Usuario.query.delete()
        Movimiento.query.delete()

    def actuar(self, client, id_movimiento, token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.get(f'/movimientos/{id_movimiento}', headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_retorna_200_si_movimiento_pertenece_a_propiedad_usuario_token(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.movimiento_reserva.id, token_usuario_1)
        assert self.respuesta.status_code == 200

    def test_retorna_movimiento_de_propiedad(self, client):
        movimiento_schema = MovimientoSchema()
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.movimiento_reserva.id, token_usuario_1)
        assert movimiento_schema.dump(self.movimiento_reserva) == self.respuesta_json

    def test_retorna_404_si_movimiento_no_es_de_propiedad_del_usuario(self, client):
        token_usuario_2 = create_access_token(identity=self.usuario_2.id)
        self.actuar(client, self.movimiento_reserva.id, token_usuario_2)
        assert self.respuesta.status_code == 404
        assert self.respuesta_json == {'mensaje': 'movimiento no encontrado'}

    def test_retorna_401_token_no_enviado(self, client):
        self.actuar(client, 123)
        assert self.respuesta.status_code == 401
