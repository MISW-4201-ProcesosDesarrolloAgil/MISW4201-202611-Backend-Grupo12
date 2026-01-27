from datetime import datetime
from unittest import TestCase
from modelos import Propiedad, Reserva, Banco, db

class TestModeloReserva(TestCase):

    def setUp(self):
        self.propiedad = Propiedad(nombre_propiedad='propiedad cerca a la quebrada', ciudad='Boyaca', municipio='Paipa',
                              direccion='Vereda Toibita', nombre_propietario='Jorge', numero_contacto='1234567', banco=Banco.BANCOLOMBIA,
                              numero_cuenta='000033322255599', id_usuario=3)
        db.session.add(self.propiedad)
        db.session.commit()

        reserva = Reserva(nombre='Julio Hernandez', fecha_ingreso=datetime.strptime('2023-01-03', '%Y-%m-%d'),
                          fecha_salida=datetime.strptime('2023-01-06', '%Y-%m-%d'), plataforma_reserva='Booking', total_reserva=568000,
                          comision='74800', id_propiedad=self.propiedad.id)
        db.session.add(reserva)
        db.session.commit()

    def tearDown(self):
        db.session.rollback()
        Propiedad.query.delete()
        Reserva.query.delete()

    def test_crea_solo_un_registro_en_db(self):
        reservas_en_db = Reserva.query.all()
        self.assertEqual(len(reservas_en_db), 1)

    def test_registro_info_correcta(self):
        reserva_db = Reserva.query.filter(Reserva.nombre == 'Julio Hernandez').first()
        self.assertIn('2023-01-03', str(reserva_db.fecha_ingreso))
        self.assertIn('2023-01-06', str(reserva_db.fecha_salida))
        self.assertEqual(reserva_db.plataforma_reserva, 'Booking')
        self.assertEqual(reserva_db.total_reserva, 568000)
        self.assertEqual(reserva_db.comision, 74800)
        self.assertEqual(reserva_db.id_propiedad, self.propiedad.id)
