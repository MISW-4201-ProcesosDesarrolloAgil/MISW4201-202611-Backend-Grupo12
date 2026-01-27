from datetime import datetime
from unittest import TestCase
from modelos import Usuario, Propiedad, Movimiento, Banco, TipoMovimiento, db


class TestModeloMovimiento(TestCase):

    def setUp(self):
        usuario = Usuario(usuario="usuario_test", contrasena='123456')
        db.session.add(usuario)
        db.session.commit()

        self.propiedad = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=usuario.id)
        db.session.add(self.propiedad)
        db.session.commit()

        self.movimiento = Movimiento(fecha=datetime.strptime('2023-01-06', '%Y-%m-%d'), valor=12345.25,
                                concepto=Movimiento.CONCEPTO_RESERVA, tipo_movimiento=TipoMovimiento.INGRESO, id_propiedad=self.propiedad.id)
        db.session.add(self.movimiento)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        Usuario.query.delete()
        Propiedad.query.delete()
        Movimiento.query.delete()

    def test_solo_un_registro_es_creado(self):
        movimientos_en_db = Movimiento.query.all()
        self.assertEqual(len(movimientos_en_db), 1)

    def test_registro_contiene_info_correcta(self):
        movimiento_db = Movimiento.query.filter(Movimiento.id == self.movimiento.id).first()
        self.assertEqual(movimiento_db.valor, 12345.25)
        self.assertEqual(movimiento_db.tipo_movimiento, TipoMovimiento.INGRESO)
        self.assertEqual(movimiento_db.concepto, Movimiento.CONCEPTO_RESERVA)
        self.assertIn('2023-01-06', str(movimiento_db.fecha))
        self.assertEqual(movimiento_db.id_propiedad, self.propiedad.id)