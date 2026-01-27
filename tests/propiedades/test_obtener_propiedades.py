from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Banco, db, PropiedadSchema


class TestObtenerPropiedades:

    def setup_method(self):
        self.usuario_1 = Usuario(usuario='usuario_1', contrasena='123456')
        self.usuario_2 = Usuario(usuario='usuario_2', contrasena='123456')
        self.usuario_3 = Usuario(usuario='usuario_3', contrasena='123456')
        db.session.add(self.usuario_1)
        db.session.add(self.usuario_2)
        db.session.add(self.usuario_3)
        db.session.commit()

        self.propiedad_1_usu_1 = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge Loaiza', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=self.usuario_1.id)
        self.propiedad_2_usu_1 = Propiedad(nombre_propiedad='Apto edificio Alto', ciudad='Bogota',
                              direccion='cra 100#7-21 apto 1302', nombre_propietario='Carlos Julio', numero_contacto='666777999', banco=Banco.NEQUI,
                              numero_cuenta='3122589635', id_usuario=self.usuario_1.id)
        self.propiedad_1_usu_2 = Propiedad(nombre_propiedad='Apartaestudio', ciudad='Medellin',
                              direccion='Cra 25#32-48 apto 305', nombre_propietario='Maria Torres', numero_contacto='999999', banco=Banco.DAVIPLATA,
                              numero_cuenta='3114896525', id_usuario=self.usuario_2.id)
        
        db.session.add(self.propiedad_1_usu_1)
        db.session.add(self.propiedad_1_usu_2)
        db.session.add(self.propiedad_2_usu_1)
        db.session.commit()

    def actuar(self, client, token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.get('/propiedades', headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_retorna_lista(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, token=token_usuario_1)
        assert isinstance(self.respuesta_json, list)

    def test_retorna_solo_propiedades_del_usuario_del_token(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, token=token_usuario_1)
        schema = PropiedadSchema()
        assert len(self.respuesta_json) == 2
        assert schema.dump(self.propiedad_1_usu_1) in self.respuesta_json
        assert schema.dump(self.propiedad_2_usu_1) in self.respuesta_json

    def test_retorna_lista_vacia_usuario_sin_propiedades(self, client):
        token_usuario_3 = create_access_token(identity=self.usuario_3.id)
        self.actuar(client, token=token_usuario_3)
        assert self.respuesta_json == []
        assert self.respuesta.status_code == 200

    def test_retorna_401_request_sin_token(self, client):
        self.actuar(client)
        assert self.respuesta.status_code == 401
