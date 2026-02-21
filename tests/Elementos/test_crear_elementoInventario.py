import json
from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Banco, Zona, ZonaPosible, ElementoInventario, db

class TestCrearElementoInventario:

    def setup_method(self):
        # 1. Crear usuarios
        self.usuario_1 = Usuario(usuario='usuario_1', contrasena='123456')
        self.usuario_2 = Usuario(usuario='usuario_2', contrasena='123456')
        db.session.add(self.usuario_1)
        db.session.add(self.usuario_2)
        db.session.commit()

        # 2. Crear propiedades
        self.propiedad_1_usu_1 = Propiedad(
            nombre_propiedad='Casa de playa', 
            ciudad='Boyaca', 
            municipio='Paipa',
            direccion='Vereda Toibita', 
            nombre_propietario='Jorge Loaiza', 
            numero_contacto='1234567', 
            banco=Banco.BANCOLOMBIA,
            numero_cuenta='000033322255599', 
            id_usuario=self.usuario_1.id
        )
        db.session.add(self.propiedad_1_usu_1)
        db.session.commit()

        # 3. Crear zona en la propiedad
        self.zona_cocina = Zona(
            nombre_zona=ZonaPosible.COCINA,
            descripcion='Cocina de la casa',
            id_propiedad=self.propiedad_1_usu_1.id
        )
        db.session.add(self.zona_cocina)
        db.session.commit()

        # 4. Datos para crear elemento
        self.datos_elemento = {
            'nombre_elemento': 'Horno Microondas',
            'descripcion': 'Elemento de cocina',
            'cantidad': 1,
            'fecha_registro': '2023-01-06T15:00:00'
        }

    def teardown_method(self):
        db.session.rollback()
        ElementoInventario.query.delete()
        Zona.query.delete()
        Propiedad.query.delete()
        Usuario.query.delete()

    def actuar(self, client, id_zona, datos_elemento=None, token=None):
        headers = {'Content-Type': 'application/json'}
        datos_elemento = datos_elemento or self.datos_elemento
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.post(
            f'/zonas/{id_zona}/elementos',
            data=json.dumps(datos_elemento), 
            headers=headers
        )
        self.respuesta_json = self.respuesta.json

    def test_crear_elemento_retorna_201(self, client):
        token = create_access_token(identity=str(self.usuario_1.id))
        self.actuar(client, self.zona_cocina.id, self.datos_elemento, token)
        assert self.respuesta.status_code == 201

    def test_crear_elemento_retorna_datos_correctos(self, client):
        token = create_access_token(identity=str(self.usuario_1.id))
        self.actuar(client, self.zona_cocina.id, self.datos_elemento, token)
        assert self.respuesta_json['nombre_elemento'] == 'Horno Microondas'
        assert self.respuesta_json['descripcion'] == 'Elemento de cocina'
        assert self.respuesta_json['cantidad'] == 1

    def test_crear_elemento_crea_registro_en_db(self, client):
        token = create_access_token(identity=str(self.usuario_1.id))
        self.actuar(client, self.zona_cocina.id, self.datos_elemento, token)
        elemento_db = ElementoInventario.query.filter(
            ElementoInventario.id_zona == self.zona_cocina.id
        ).first()
        assert elemento_db is not None
        assert elemento_db.nombre_elemento == 'Horno Microondas'

    def test_crear_elemento_sin_token_retorna_401(self, client):
        self.actuar(client, self.zona_cocina.id, self.datos_elemento)
        assert self.respuesta.status_code == 401

    def test_crear_elemento_zona_inexistente_retorna_404(self, client):
        token = create_access_token(identity=str(self.usuario_1.id))
        self.actuar(client, 999, self.datos_elemento, token)
        assert self.respuesta.status_code == 404


