import datetime
import json
import pytest
from modelos import db, Usuario, Propiedad, Movimiento, TipoMovimiento


@pytest.fixture()
def usuario_prueba(app):
    usuario = Usuario(usuario='usuario_ingreso_test', contrasena='contrasena123')
    db.session.add(usuario)
    db.session.commit()
    return usuario


@pytest.fixture()
def propiedad_prueba(app, usuario_prueba):
    propiedad = Propiedad(
        nombre_propiedad='Casa Test',
        ciudad='Bogotá',
        municipio='Bogotá',
        direccion='Calle 1 # 1',
        nombre_propietario='Juan Pérez',
        numero_contacto='3101234567',
        id_usuario=usuario_prueba.id
    )
    db.session.add(propiedad)
    db.session.commit()
    return propiedad


@pytest.fixture()
def ingresos_prueba(app, propiedad_prueba):
    """Crea varios ingresos de prueba para la propiedad"""
    fecha_actual = datetime.datetime.now()
    
    ingreso1 = Movimiento(
        fecha=fecha_actual,
        concepto='RESERVA',
        valor=1000000.0,
        tipo_movimiento=TipoMovimiento.INGRESO,
        id_propiedad=propiedad_prueba.id
    )
    
    ingreso2 = Movimiento(
        fecha=fecha_actual - datetime.timedelta(days=5),
        concepto='RESERVA',
        valor=500000.0,
        tipo_movimiento=TipoMovimiento.INGRESO,
        id_propiedad=propiedad_prueba.id
    )
    
    ingreso3 = Movimiento(
        fecha=fecha_actual - datetime.timedelta(days=10),
        concepto='AJUSTE',
        valor=200000.0,
        tipo_movimiento=TipoMovimiento.INGRESO,
        id_propiedad=propiedad_prueba.id
    )
    
    db.session.add_all([ingreso1, ingreso2, ingreso3])
    db.session.commit()
    
    return [ingreso1, ingreso2, ingreso3]


class TestVistaIngresos:
    """Tests para el endpoint de obtener ingresos de una propiedad"""
    
    def test_obtener_ingresos_propiedad(self, client, usuario_prueba, propiedad_prueba, ingresos_prueba):
        """Verifica que se obtienen todos los ingresos de una propiedad"""
        # Login del usuario
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_ingreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        
        assert respuesta_login.status_code == 200
        token = respuesta_login.json['token']
        
        # Obtener ingresos
        respuesta = client.get(
            f'/propiedades/{propiedad_prueba.id}/ingresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        
        assert 'ingresos' in datos
        assert 'total' in datos
        assert 'cantidad' in datos
        assert len(datos['ingresos']) == 3
        assert datos['total'] == 1700000.0  # suma de todos los ingresos
        assert datos['cantidad'] == 3
    
    def test_obtener_ingresos_sin_autenticacion(self, client, propiedad_prueba):
        """Verifica que se requiere autenticación"""
        respuesta = client.get(f'/propiedades/{propiedad_prueba.id}/ingresos')
        assert respuesta.status_code == 401
    
    def test_obtener_ingresos_propiedad_no_existe(self, client, usuario_prueba):
        """Verifica que devuelve 404 si la propiedad no existe"""
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_ingreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        respuesta = client.get(
            '/propiedades/999/ingresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 404
        assert json.loads(respuesta.data)['mensaje'] == 'propiedad no encontrada'
    
    def test_obtener_ingresos_con_filtro_mes_anio(self, client, usuario_prueba, propiedad_prueba):
        """Verifica que se puede filtrar ingresos por mes y año"""
        # Crear ingresos en diferentes meses
        fecha_actual = datetime.datetime.now()
        
        ingreso_mes_actual = Movimiento(
            fecha=fecha_actual,
            concepto='RESERVA',
            valor=1000000.0,
            tipo_movimiento=TipoMovimiento.INGRESO,
            id_propiedad=propiedad_prueba.id
        )
        
        ingreso_mes_pasado = Movimiento(
            fecha=fecha_actual.replace(month=fecha_actual.month - 1 if fecha_actual.month > 1 else 12),
            concepto='RESERVA',
            valor=500000.0,
            tipo_movimiento=TipoMovimiento.INGRESO,
            id_propiedad=propiedad_prueba.id
        )
        
        db.session.add_all([ingreso_mes_actual, ingreso_mes_pasado])
        db.session.commit()
        
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_ingreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        # Filtrar por mes actual
        respuesta = client.get(
            f'/propiedades/{propiedad_prueba.id}/ingresos?mes={fecha_actual.month}&anio={fecha_actual.year}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        
        assert datos['cantidad'] == 1
        assert datos['total'] == 1000000.0
    
    def test_obtener_ingresos_vacia(self, client, usuario_prueba, propiedad_prueba):
        """Verifica que devuelve lista vacía si no hay ingresos"""
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_ingreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        respuesta = client.get(
            f'/propiedades/{propiedad_prueba.id}/ingresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        
        assert datos['cantidad'] == 0
        assert datos['total'] == 0
        assert len(datos['ingresos']) == 0
    
    def test_usuario_no_ve_ingresos_otras_propiedades(self, app, client):
        """Verifica que un usuario solo ve ingresos de sus propias propiedades"""
        # Crear dos usuarios y propiedades
        usuario1 = Usuario(usuario='usuario1_ingreso', contrasena='pass123')
        usuario2 = Usuario(usuario='usuario2_ingreso', contrasena='pass123')
        db.session.add_all([usuario1, usuario2])
        db.session.commit()
        
        propiedad1 = Propiedad(
            nombre_propiedad='Casa User1',
            ciudad='Bogotá',
            municipio='Bogotá',
            direccion='Calle 1',
            nombre_propietario='User1',
            numero_contacto='3101111111',
            id_usuario=usuario1.id
        )
        
        propiedad2 = Propiedad(
            nombre_propiedad='Casa User2',
            ciudad='Medellín',
            municipio='Medellín',
            direccion='Carrera 2',
            nombre_propietario='User2',
            numero_contacto='3102222222',
            id_usuario=usuario2.id
        )
        
        db.session.add_all([propiedad1, propiedad2])
        db.session.commit()
        
        # Crear ingreso para propiedad2
        ingreso = Movimiento(
            fecha=datetime.datetime.now(),
            concepto='RESERVA',
            valor=1000000.0,
            tipo_movimiento=TipoMovimiento.INGRESO,
            id_propiedad=propiedad2.id
        )
        db.session.add(ingreso)
        db.session.commit()
        
        # Login usuario1 e intentar acceder a propiedad2
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario1_ingreso', 'contrasena': 'pass123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        respuesta = client.get(
            f'/propiedades/{propiedad2.id}/ingresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 404
