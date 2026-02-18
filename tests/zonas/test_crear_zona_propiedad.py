import json

from flask_jwt_extended import create_access_token
from modelos import Banco, Usuario, Propiedad, db, Zona, ZonaPosible


class TestCrearZonaPropiedad:

    def setup_method(self):
        self.usuario_1 = Usuario(usuario='usuario_1', contrasena='123456')
        self.usuario_2 = Usuario(usuario='usuario_2', contrasena='123456')
        db.session.add(self.usuario_1)
        db.session.add(self.usuario_2)
        db.session.commit()

        self.propiedad_1_usu_1 = Propiedad(
            nombre_propiedad='Casa en la montaña',
            ciudad='Boyaca',
            municipio='Paipa',
            direccion='Vereda Toibita',
            nombre_propietario='Jorge Loaiza',
            numero_contacto='1234567',
            banco=Banco.BANCOLOMBIA,
            numero_cuenta='000033322255599',
            id_usuario=self.usuario_1.id
        )
        self.propiedad_1_usu_2 = Propiedad(
            nombre_propiedad='Apto edificio Alto',
            ciudad='Bogota',
            direccion='cra 100#7-21 apto 1302',
            nombre_propietario='Carlos Julio',
            numero_contacto='666777999',
            banco=Banco.NEQUI,
            numero_cuenta='3122589635',
            id_usuario=self.usuario_2.id
        )
        db.session.add(self.propiedad_1_usu_1)
        db.session.add(self.propiedad_1_usu_2)
        db.session.commit()

        self.datos_zona = {
            'nombre_zona': ZonaPosible.COCINA.value,
            'descripcion': 'Cocina integral con estufa de gas'
        }

    def teardown_method(self):
        db.session.rollback()
        Zona.query.delete()
        Propiedad.query.delete()
        Usuario.query.delete()

    def actuar(self, client, id_propiedad, datos_zona=None, token=None):
        headers = {'Content-Type': 'application/json'}
        datos_zona = datos_zona or self.datos_zona
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.post(
            f'/propiedades/{id_propiedad}/zonas',
            data=json.dumps(datos_zona),
            headers=headers
        )
        self.respuesta_json = self.respuesta.json

    def test_crear_zona_propiedad_del_usuario_retorna_201(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id)
        self.actuar(client, self.propiedad_1_usu_1.id, self.datos_zona, token_usuario_1)
        self.respuesta.status_code == 201