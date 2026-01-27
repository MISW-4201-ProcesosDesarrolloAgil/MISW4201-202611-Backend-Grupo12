import enum
from sqlalchemy import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()


class TipoMovimiento(enum.Enum):
    INGRESO = 'INGRESO'
    EGRESO = 'EGRESO'


class Banco(enum.Enum):
    BANCO_BBVA                      = 'BANCO_BBVA'
    BANCAMIA                        = 'BANCAMIA'
    BANCO_AGRARIO                   = 'BANCO_AGRARIO'
    BANCO_AV_VILLAS                 = 'BANCO_AV_VILLAS'
    BANCO_CAJA_SOCIAL               = 'BANCO_CAJA_SOCIAL'
    BANCO_CITIBANK                  = 'BANCO_CITIBANK'
    BANCO_COOPERATIVO_COOPCENTRAL   = 'BANCO_COOPERATIVO_COOPCENTRAL'
    BANCO_CREDIFINANCIERA           = 'BANCO_CREDIFINANCIERA'
    DAVIPLATA                       = 'DAVIPLATA'
    BANCO_DE_BOGOTA                 = 'BANCO_DE_BOGOTA'
    BANCO_DE_OCCIDENTE              = 'BANCO_DE_OCCIDENTE'
    BANCO_FALABELLA                 = 'BANCO_FALABELLA'
    BANCO_FINANDINA                 = 'BANCO_FINANDINA'
    BANCO_GNB_SUDAMERIS             = 'BANCO_GNB_SUDAMERIS'
    BANCO_ITAU                      = 'BANCO_ITAU'
    BANCO_MUNDO_MUJER               = 'BANCO_MUNDO_MUJER'
    BANCO_PICHINCHA                 = 'BANCO_PICHINCHA'
    BANCO_POPULAR                   = 'BANCO_POPULAR'
    BANCO_PROCREDIT                 = 'BANCO_PROCREDIT'
    BANCO_SANTANDER                 = 'BANCO_SANTANDER'
    BANCO_SERFINANZA                = 'BANCO_SERFINANZA'
    BANCO_TEQUENDAMA                = 'BANCO_TEQUENDAMA'
    BANCO_WWB                       = 'BANCO_WWB'
    BANCOLDEX                       = 'BANCOLDEX'
    BANCOLOMBIA                     = 'BANCOLOMBIA'
    BANCOMPARTIR                    = 'BANCOMPARTIR'
    BANCOOMEVA                      = 'BANCOOMEVA'
    COLTEFINANCIERA                 = 'COLTEFINANCIERA'
    CONFIAR_COOPERATIVA_FINANCIERA  = 'CONFIAR_COOPERATIVA_FINANCIERA'
    COOFIANTIOQUIA                  = 'COOFIANTIOQUIA'
    COOFINEP_COOPERATIVA_FINANCIERA = 'COOFINEP_COOPERATIVA_FINANCIERA'
    COTRAFA_COOPERATIVA_FINANCIERA  = 'COTRAFA_COOPERATIVA_FINANCIERA'
    FINANCIERA_JURISCOOP            = 'FINANCIERA_JURISCOOP'
    GIROS_Y_FINANZAS_CF             = 'GIROS_Y_FINANZAS_CF'
    IRIS                            = 'IRIS'
    LULO_BANK                       = 'LULO_BANK'
    MOVii                           = 'MOVii'
    SCOTIABANK_COLPATRIA            = 'SCOTIABANK_COLPATRIA'
    SERVIFINANSA                    = 'SERVIFINANSA'
    RAPPIPAY                        = 'RAPPIPAY'
    NEQUI                           = 'NEQUI'


class Propiedad(db.Model):
    __table_args__ = (UniqueConstraint('direccion', 'ciudad', 'municipio', name='unique_address'),)

    id = db.Column(db.Integer, primary_key=True)
    nombre_propiedad = db.Column(db.String(128), nullable=False)
    ciudad = db.Column(db.String(128), nullable=False)
    municipio = db.Column(db.String(128), nullable=True)
    direccion = db.Column(db.String(128), nullable=False)
    nombre_propietario = db.Column(db.String(128), nullable=False)
    numero_contacto = db.Column(db.String(15), nullable=False)
    banco = db.Column(db.Enum(Banco), nullable=True)
    numero_cuenta = db.Column(db.String(32), nullable=True)
    movimientos = db.relationship('Movimiento', cascade='all, delete, delete-orphan')
    reservas = db.relationship('Reserva', cascade='all, delete, delete-orphan')
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)


class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    fecha_ingreso = db.Column(db.DateTime, nullable=False)
    fecha_salida = db.Column(db.DateTime, nullable=False)
    plataforma_reserva = db.Column(db.String(50), nullable=False)
    total_reserva = db.Column(db.Float, nullable=False)
    comision = db.Column(db.Float, nullable=False)
    numero_personas = db.Column(db.Integer, nullable=False, default=0)
    observaciones = db.Column(db.String(128))
    id_propiedad = db.Column(db.Integer, db.ForeignKey('propiedad.id'))
    movimientos = db.relationship('Movimiento', cascade='all, delete, delete-orphan')


class Movimiento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, nullable=False)
    concepto = db.Column(db.String(128), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    id_reserva = db.Column(db.Integer, db.ForeignKey('reserva.id'), nullable=True)
    tipo_movimiento = db.Column(db.Enum(TipoMovimiento), nullable=False)
    id_propiedad = db.Column(db.Integer, db.ForeignKey('propiedad.id'))
    
    CONCEPTO_RESERVA = 'RESERVA'
    CONCEPTO_COMISION = 'COMISION'
    

class Usuario(db.Model):
    __table_args__ = (UniqueConstraint('usuario', name='unique_username'),)
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    contrasena = db.Column(db.String(50), nullable=False)
    propiedades = db.relationship('Propiedad', cascade='all, delete, delete-orphan')


class ReservaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Reserva
        include_relationships = True
        include_fk = True
        load_instance = True


class PropiedadSchema(SQLAlchemyAutoSchema):
    banco = fields.Enum(Banco, by_value=True, allow_none=True)
    class Meta:
        model = Propiedad
        include_relationships = True
        load_instance = True


class MovimientoSchema(SQLAlchemyAutoSchema):
    tipo_movimiento = fields.Enum(TipoMovimiento, by_value=True)
    id_reserva = fields.Integer(allow_none=True)
    id_propiedad = fields.Integer()
    
    class Meta:
        model = Movimiento
        include_relationships = True
        load_instance = True


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
        exclude = ('contrasena',)
