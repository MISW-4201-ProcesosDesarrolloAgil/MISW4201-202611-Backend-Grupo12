import json

from flask_jwt_extended import create_access_token
from modelos import Usuario, Propiedad, Banco, db


class TestActualizarPropiedad:

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

    def teardown_method(self):
        db.session.rollback()
        Usuario.query.delete()
        
    def actuar(self, datos_propiedad, propiedad_id, client, token=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers.update({'Authorization': f'Bearer {token}'})
        self.respuesta = client.put(f'/propiedades/{propiedad_id}', data=json.dumps(datos_propiedad), headers=headers)
        self.respuesta_json = self.respuesta.json

    def test_retorna_200_al_actualizar_propiedad(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id) 
        self.actuar(
            {
                'nombre_propiedad': 'nombre actualizado',
                'direccion': 'nueva direccion'
            },
            self.propiedad_1_usu_1.id,
            client,
            token_usuario_1
        )
        assert self.respuesta.status_code == 200

    def test_retorna_401_no_token(self, client):
        self.actuar(
            {
                'nombre_propiedad': 'nombre actualizado',
                'direccion': 'nueva direccion'
            },
            self.propiedad_1_usu_1.id,
            client,
        )
        assert self.respuesta.status_code == 401

    def test_actualiza_solo_campos_enviados(self, client):
        token_usuario_1 = create_access_token(identity=self.usuario_1.id) 
        self.actuar(
            {
                'nombre_propiedad': 'nombre actualizado',
                'direccion': 'nueva direccion'
            },
            self.propiedad_1_usu_1.id,
            client,
            token_usuario_1
        )
        propiedad_db = Propiedad.query.filter(Propiedad.id == self.propiedad_1_usu_1.id).first()
        assert propiedad_db.nombre_propiedad == 'nombre actualizado'
        assert propiedad_db.direccion == 'nueva direccion'
        assert propiedad_db.ciudad == 'Boyaca'
        assert propiedad_db.municipio == 'Paipa'

    def test_retorna_404_si_propiedad_no_es_del_usuario(self, client):
        token_usuario_2 = create_access_token(identity=self.usuario_2.id) 
        self.actuar(
            {
                'nombre_propiedad': 'nombre actualizado',
                'direccion': 'nueva direccion'
            },
            self.propiedad_1_usu_1.id,
            client,
            token_usuario_2
        )
        assert self.respuesta.status_code == 404
        assert self.respuesta_json == {"mensaje": "propiedad no encontrada"}
