import json

from flask_jwt_extended import create_access_token
from modelos import Banco, Usuario, Propiedad, db, Zona,ZonaPosible


class TestCrearZonaPropiedad:

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
        self.zona_propiedad = {
            'nombre_zona': ZonaPosible.COCINA.value,
            'descripcion': 'Zona de la cocina con todos los electrodomesticos necesarios',
        }
    def teardown_method(self):
        db.session.rollback()
        Usuario.query.delete()
        Propiedad.query.delete()
        Zona.query.delete()

    def actuar(self, client, datos_propiedad=None, token=None):
        datos_propiedad = datos_propiedad or self.datos_propiedad
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesa = client.post('/propiedades', data=json.dumps(datos_propiedad), headers=headers)
        self.respuesta_json = self.respuesa.json
    
    def test_retorna_201_si_es_exitoso(self, client):
        self.actuar(client, token=self.usuario_token)
        propiedad_id = self.respuesta_json["id"]
        response_zona = client.post(f'/propiedades/{propiedad_id}/zonas', data=json.dumps(self.zona_propiedad), headers={'Authorization': f'Bearer {self.usuario_token}', 'Content-Type': 'application/json'})
        assert response_zona.status_code == 201