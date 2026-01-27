from unittest import TestCase
from modelos import Usuario, db
from sqlalchemy import exc


class TestCreateUser(TestCase):

    def tearDown(self):
        db.session.rollback()
        Usuario.query.delete()

    def test_solo_un_usuario_es_creado_en_db(self):
        new_user = Usuario(usuario='test_user', contrasena='123456')
        db.session.add(new_user)
        db.session.commit()

        users_in_db = Usuario.query.all()
        self.assertEqual(len(users_in_db), 1)

    def test_usuario_esperado_es_creado(self):
        new_user = Usuario(usuario='test_user', contrasena='123456')
        db.session.add(new_user)
        db.session.commit()

        user_from_db = Usuario.query.filter(Usuario.usuario=='test_user').first()
        self.assertEqual(user_from_db.contrasena, '123456')

    def test_dispara_un_error_de_integridad(self):
        first_user = Usuario(usuario='test_user', contrasena='123456')
        db.session.add(first_user)
        db.session.commit()
        with self.assertRaises(exc.IntegrityError):
            user_same_username = Usuario(usuario='test_user', contrasena='abcdef')
            db.session.add(user_same_username)
            db.session.commit()

    def test_campos_no_pueden_ser_nullos(self):
        user = Usuario()
        with self.assertRaises(exc.IntegrityError):
            db.session.add(user)
            db.session.commit()
