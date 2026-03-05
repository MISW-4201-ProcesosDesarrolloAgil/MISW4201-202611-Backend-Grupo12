import datetime
import json
import pytest
from modelos import db, Usuario, Propiedad, Movimiento, TipoMovimiento


@pytest.fixture()
def usuario_prueba(app):
    usuario = Usuario(usuario='usuario_egreso_test', contrasena='contrasena123')
    db.session.add(usuario)
    db.session.commit()
    return usuario


@pytest.fixture()
def propiedad_prueba(app, usuario_prueba):
    propiedad = Propiedad(
        nombre_propiedad='Casa Test Egresos',
        ciudad='Bogotá',
        municipio='Bogotá',
        direccion='Calle 2 # 2',
        nombre_propietario='Juan Pérez',
        numero_contacto='3101234567',
        id_usuario=usuario_prueba.id
    )
    db.session.add(propiedad)
    db.session.commit()
    return propiedad


@pytest.fixture()
def egresos_prueba(app, propiedad_prueba):
    """Crea varios egresos de prueba para la propiedad"""
    fecha_actual = datetime.datetime.now()
    
    egreso1 = Movimiento(
        fecha=fecha_actual,
        concepto='MANTENIMIENTO',
        valor=200000.0,
        tipo_movimiento=TipoMovimiento.EGRESO,
        id_propiedad=propiedad_prueba.id
    )
    
    egreso2 = Movimiento(
        fecha=fecha_actual - datetime.timedelta(days=5),
        concepto='SERVICIOS',
        valor=150000.0,
        tipo_movimiento=TipoMovimiento.EGRESO,
        id_propiedad=propiedad_prueba.id
    )
    
    egreso3 = Movimiento(
        fecha=fecha_actual - datetime.timedelta(days=10),
        concepto='IMPUESTOS',
        valor=300000.0,
        tipo_movimiento=TipoMovimiento.EGRESO,
        id_propiedad=propiedad_prueba.id
    )
    
    db.session.add_all([egreso1, egreso2, egreso3])
    db.session.commit()
    
    return [egreso1, egreso2, egreso3]


class TestVistaEgresos:
    """Tests para el endpoint de obtener egresos de una propiedad"""
    
    def test_obtener_egresos_propiedad(self, client, usuario_prueba, propiedad_prueba, egresos_prueba):
        """Verifica que se obtienen todos los egresos de una propiedad"""
        # Login del usuario
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_egreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        
        assert respuesta_login.status_code == 200
        token = respuesta_login.json['token']
        
        # Obtener egresos
        respuesta = client.get(
            f'/propiedades/{propiedad_prueba.id}/egresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        
        assert 'egresos' in datos
        assert 'total' in datos
        assert 'cantidad' in datos
        assert len(datos['egresos']) == 3
        assert datos['total'] == 650000.0  # suma de todos los egresos
        assert datos['cantidad'] == 3
    
    def test_obtener_egresos_sin_autenticacion(self, client, propiedad_prueba):
        """Verifica que se requiere autenticación"""
        respuesta = client.get(f'/propiedades/{propiedad_prueba.id}/egresos')
        assert respuesta.status_code == 401
    
    def test_obtener_egresos_propiedad_no_existe(self, client, usuario_prueba):
        """Verifica que devuelve 404 si la propiedad no existe"""
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_egreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        respuesta = client.get(
            '/propiedades/999/egresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 404
        assert json.loads(respuesta.data)['mensaje'] == 'propiedad no encontrada'
    
    def test_obtener_egresos_con_filtro_mes_anio(self, client, usuario_prueba, propiedad_prueba):
        """Verifica que se puede filtrar egresos por mes y año"""
        # Crear egresos en diferentes meses
        fecha_actual = datetime.datetime.now()
        
        egreso_mes_actual = Movimiento(
            fecha=fecha_actual,
            concepto='MANTENIMIENTO',
            valor=200000.0,
            tipo_movimiento=TipoMovimiento.EGRESO,
            id_propiedad=propiedad_prueba.id
        )
        
        egreso_mes_pasado = Movimiento(
            fecha=fecha_actual.replace(month=fecha_actual.month - 1 if fecha_actual.month > 1 else 12),
            concepto='SERVICIOS',
            valor=150000.0,
            tipo_movimiento=TipoMovimiento.EGRESO,
            id_propiedad=propiedad_prueba.id
        )
        
        db.session.add_all([egreso_mes_actual, egreso_mes_pasado])
        db.session.commit()
        
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_egreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        # Filtrar por mes actual
        respuesta = client.get(
            f'/propiedades/{propiedad_prueba.id}/egresos?mes={fecha_actual.month}&anio={fecha_actual.year}',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        
        assert datos['cantidad'] == 1
        assert datos['total'] == 200000.0
    
    def test_obtener_egresos_vacia(self, client, usuario_prueba, propiedad_prueba):
        """Verifica que devuelve lista vacía si no hay egresos"""
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario_egreso_test', 'contrasena': 'contrasena123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        respuesta = client.get(
            f'/propiedades/{propiedad_prueba.id}/egresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        
        assert datos['cantidad'] == 0
        assert datos['total'] == 0
        assert len(datos['egresos']) == 0
    
    def test_usuario_no_ve_egresos_otras_propiedades(self, app, client):
        """Verifica que un usuario solo ve egresos de sus propias propiedades"""
        # Crear dos usuarios y propiedades
        usuario1 = Usuario(usuario='usuario1_egreso', contrasena='pass123')
        usuario2 = Usuario(usuario='usuario2_egreso', contrasena='pass123')
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
        
        # Crear egreso para propiedad2
        egreso = Movimiento(
            fecha=datetime.datetime.now(),
            concepto='MANTENIMIENTO',
            valor=200000.0,
            tipo_movimiento=TipoMovimiento.EGRESO,
            id_propiedad=propiedad2.id
        )
        db.session.add(egreso)
        db.session.commit()
        
        # Login usuario1 e intentar acceder a propiedad2
        respuesta_login = client.post('/login', 
            json={'usuario': 'usuario1_egreso', 'contrasena': 'pass123'},
            headers={'Content-Type': 'application/json'}
        )
        token = respuesta_login.json['token']
        
        respuesta = client.get(
            f'/propiedades/{propiedad2.id}/egresos',
            headers={'Authorization': f'Bearer {token}'}
        )
        
        assert respuesta.status_code == 404
