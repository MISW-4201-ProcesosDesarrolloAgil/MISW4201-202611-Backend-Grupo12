from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy import exc
from modelos import TipoMovimiento, Movimiento, db, ReservaSchema
from vistas.utils import buscar_propiedad

reserva_schema = ReservaSchema()


class VistaReservas(Resource):

    @jwt_required()
    def post(self, id_propiedad):
        resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
        if resultado_buscar_propiedad.error:
           return resultado_buscar_propiedad.error
        
        try:
            reserva = reserva_schema.load(request.json, session=db.session)
            reserva.id_propiedad = id_propiedad
            db.session.add(reserva)
            db.session.commit()
        except ValidationError as validation_error:
            return validation_error.messages, 400
        except exc.IntegrityError:
            db.session.rollback()
            return {'mensaje': 'Hubo un error creando la reserva. Revise los datos proporcionados'}, 400

        self.crear_movimientos(reserva)
        return reserva_schema.dump(reserva), 201
    
    @jwt_required()
    def get(self, id_propiedad):
       resultado_buscar_propiedad = buscar_propiedad(id_propiedad, current_user.id)
       if resultado_buscar_propiedad.error:
           return resultado_buscar_propiedad.error
       reservas = resultado_buscar_propiedad.propiedad.reservas
       return reserva_schema.dump(reservas, many=True)

    def crear_movimientos(self, reserva):
        movimiento_ingreso = Movimiento(fecha=reserva.fecha_ingreso,
                                concepto=Movimiento.CONCEPTO_RESERVA,
                                valor=reserva.total_reserva,
                                id_reserva=reserva.id,
                                tipo_movimiento=TipoMovimiento.INGRESO,
                                id_propiedad=reserva.id_propiedad)
        movimiento_egreso = Movimiento(fecha=reserva.fecha_ingreso,
                                concepto=Movimiento.CONCEPTO_COMISION,
                                valor=reserva.comision,
                                id_reserva=reserva.id,
                                tipo_movimiento=TipoMovimiento.EGRESO,
                                id_propiedad=reserva.id_propiedad)
        db.session.add(movimiento_ingreso)
        db.session.add(movimiento_egreso)
        db.session.commit()
