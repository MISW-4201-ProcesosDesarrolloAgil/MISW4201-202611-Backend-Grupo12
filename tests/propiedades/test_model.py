from unittest import TestCase
from modelos import Propiedad, db, Usuario
from modelos.modelos import Banco


class TestModeloPropiedades(TestCase):

    def setUp(self):
        self.usuario = Usuario(usuario="usuario_test", contrasena='123456')
        db.session.add(self.usuario)
        db.session.commit()

        propiedad = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=self.usuario.id)
        db.session.add(propiedad)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        Usuario.query.delete()
        Propiedad.query.delete()

    def test_solo_un_registro_es_creado(self):
        propiedades_en_db = Propiedad.query.all()
        self.assertEqual(len(propiedades_en_db), 1)

    def test_registro_con_info_correcta_es_creado(self):
        propiedad_db = Propiedad.query.filter(Propiedad.nombre_propiedad == 'propiedad cerca a la quebrada').first()
        self.assertEqual(propiedad_db.ciudad, 'Boyaca')
        self.assertEqual(propiedad_db.municipio, 'Paipa')
        self.assertEqual(propiedad_db.direccion, 'Vereda Toibita')
        self.assertEqual(propiedad_db.nombre_propietario, 'Jorge')
        self.assertEqual(propiedad_db.numero_contacto, '1234567')
        self.assertEqual(propiedad_db.banco, Banco.BANCOLOMBIA)
        self.assertEqual(propiedad_db.numero_cuenta, '000033322255599')
        self.assertEqual(propiedad_db.id_usuario, self.usuario.id)
