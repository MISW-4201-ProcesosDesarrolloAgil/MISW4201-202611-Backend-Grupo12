from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from modelos import Movimiento, MovimientoSchema, Propiedad, TipoMovimiento, db
from vistas.utils import buscar_propiedad
from sqlalchemy import and_

movimiento_schema = MovimientoSchema()


class VistaIngresos(Resource):

    @jwt_required()
    def get(self, id_propiedad):
        """
        Obtiene los ingresos de una propiedad específica.
        Parámetros opcionales de query:
        - mes: número del mes (1-12)
        - anio: año (ej: 2026)
        """
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
            return resultado_buscar_propiedad.error
        
        # Obtener parámetros de filtro
        mes = request.args.get('mes', type=int)
        anio = request.args.get('anio', type=int)
        
        # Construir query base
        query = db.session.query(Movimiento).filter(
            and_(
                Movimiento.id_propiedad == id_propiedad,
                Movimiento.tipo_movimiento == TipoMovimiento.INGRESO
            )
        )
        
        # Aplicar filtro de período si se proporciona
        # SQLite usa strftime para funciones de fecha
        if mes is not None and anio is not None:
            query = query.filter(
                db.func.strftime('%m', Movimiento.fecha).cast(db.Integer) == mes,
                db.func.strftime('%Y', Movimiento.fecha).cast(db.Integer) == anio
            )
        elif anio is not None:
            query = query.filter(db.func.strftime('%Y', Movimiento.fecha).cast(db.Integer) == anio)
        
        ingresos = query.order_by(Movimiento.fecha.desc()).all()
        
        # Calcular total de ingresos
        total_ingresos = sum(ingreso.valor for ingreso in ingresos)
        
        return {
            'ingresos': movimiento_schema.dump(ingresos, many=True),
            'total': total_ingresos,
            'cantidad': len(ingresos)
        }
