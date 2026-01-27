import json

from flask_jwt_extended import create_access_token
from modelos import Banco, Usuario, Propiedad, db


class TestCrearPropiedad:

    def setup_method(self):
        self.usuario = Usuario(usuario='test_user', contrasena='123456')
        db.session.add(self.usuario)
        db.session.commit()
        self.usuario_token = create_access_token(identity=self.usuario.id)

        self.datos_propiedad = {
        'nombre_propiedad': 'Refugio el lago',
        'ciudad': 'Boyaca',
        'municipio': 'Paipa',
        'direccion': 'Vereda Toibita',
        'nombre_propietario': 'Juan Segura',
        'numero_contacto': '+573123334455',
        'banco': Banco.NEQUI.value,
        'numero_cuenta': '3123334455',
        }

    def teardown_method(self):
        db.session.rollback()
        Usuario.query.delete()
        Propiedad.query.delete()

    def actuar(self, client, datos_propiedad=None, token=None):
        datos_propiedad = datos_propiedad or self.datos_propiedad
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesa = client.post('/propiedades', data=json.dumps(datos_propiedad), headers=headers)
        self.respuesta_json = self.respuesa.json

    def test_retorna_201_si_es_exitoso(self, client):
        self.actuar(client, token=self.usuario_token)
        assert self.respuesa.status_code == 201

    def test_retorna_dict_si_es_exitoso(self, client):
        self.actuar(client, token=self.usuario_token)
        assert isinstance(self.respuesta_json, dict)

    def test_retorna_401_si_token_no_es_enviado(self, client):
        self.actuar(client)
        assert self.respuesa.status_code == 401

    def test_propiedad_es_creada_en_db(self, client):
        self.actuar(token=self.usuario_token, client=client)
        propiedades_en_db = Propiedad.query.all()
        assert len(propiedades_en_db) == 1
        assert self.respuesta_json["id"] == propiedades_en_db[0].id

    def test_propiedad_es_creada_para_usuario_en_token(self, client):
        self.actuar(token=self.usuario_token, client=client)
        propiedad_db = Propiedad.query.filter(Propiedad.id_usuario == self.usuario.id).first()
        assert propiedad_db

    def test_retorna_campos_esperados(self, client):
        self.actuar(token=self.usuario_token, client=client)
        assert 'nombre_propiedad' in self.respuesta_json
        assert 'ciudad' in self.respuesta_json
        assert 'municipio' in self.respuesta_json
        assert 'direccion' in self.respuesta_json
        assert 'nombre_propietario' in self.respuesta_json
        assert 'banco' in self.respuesta_json
        assert 'numero_cuenta' in self.respuesta_json
        assert 'numero_contacto' in self.respuesta_json
