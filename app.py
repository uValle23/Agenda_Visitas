import os
import sys
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)

# 🔹 Tomar siempre la variable de entorno DATABASE_URL
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    raise RuntimeError("❌ No se encontró la variable DATABASE_URL. Configúrala en Render.")

# Render a veces da postgres:// en lugar de postgresql://
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Configuración base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"✅ Conectado a: {app.config['SQLALCHEMY_DATABASE_URI']}", file=sys.stderr)

db = SQLAlchemy(app)

# ------------------------
# MODELO DE CITAS
# ------------------------
# Este modelo ha sido actualizado para incluir todos los campos del formulario HTML.
class Cita(db.Model):
    __tablename__ = 'citas'
    id = db.Column(db.Integer, primary_key=True)
    numExpediente = db.Column(db.String(50), nullable=False)
    fechaIngreso = db.Column(db.String(50), nullable=False)
    nombreAdmin = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    edad = db.Column(db.Integer, nullable=True)
    manzana = db.Column(db.String(20), nullable=True)
    lote = db.Column(db.String(20), nullable=True)
    sector = db.Column(db.String(100), nullable=True)
    asuntos = db.Column(db.Text, nullable=True)  # Guardamos la lista de asuntos como un JSON string
    fechaVisita = db.Column(db.String(50), nullable=False)
    horaVisita = db.Column(db.String(20), nullable=False)
    programador = db.Column(db.String(100), nullable=False)
    fechaCreacion = db.Column(db.String(100), nullable=False)

with app.app_context():
    db.create_all()

# ------------------------
# VISTA PRINCIPAL
# ------------------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# ------------------------
# API REST
# ------------------------

# 🔹 Obtener todas las citas
@app.route("/api/citas", methods=["GET"])
def get_citas():
    citas = Cita.query.all()
    citas_list = []
    for c in citas:
        citas_list.append({
            "id": c.id,
            "numExpediente": c.numExpediente,
            "fechaIngreso": c.fechaIngreso,
            "nombreAdmin": c.nombreAdmin,
            "dni": c.dni,
            "edad": c.edad,
            "manzana": c.manzana,
            "lote": c.lote,
            "sector": c.sector,
            "asuntos": json.loads(c.asuntos) if c.asuntos else [], # Convertimos de JSON string a lista
            "fechaVisita": c.fechaVisita,
            "horaVisita": c.horaVisita,
            "programador": c.programador,
            "fechaCreacion": c.fechaCreacion
        })
    return jsonify(citas_list)

# 🔹 Registrar nueva cita
@app.route("/api/citas", methods=["POST"])
def add_cita():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos"}), 400

    # Creamos una nueva cita con los datos del JSON
    nueva_cita = Cita(
        numExpediente=data.get("numExpediente"),
        fechaIngreso=data.get("fechaIngreso"),
        nombreAdmin=data.get("nombreAdmin"),
        dni=data.get("dni"),
        edad=data.get("edad"),
        manzana=data.get("manzana"),
        lote=data.get("lote"),
        sector=data.get("sector"),
        asuntos=json.dumps(data.get("asuntos")), # Convertimos la lista a JSON string para guardar
        fechaVisita=data.get("fechaVisita"),
        horaVisita=data.get("horaVisita"),
        programador=data.get("programador"),
        fechaCreacion=data.get("fechaCreacion")
    )
    
    db.session.add(nueva_cita)
    db.session.commit()

    return jsonify({
        "message": "Cita registrada con éxito",
        "cita": {
            "id": nueva_cita.id,
            "numExpediente": nueva_cita.numExpediente,
            "fechaIngreso": nueva_cita.fechaIngreso,
            "nombreAdmin": nueva_cita.nombreAdmin,
            "dni": nueva_cita.dni,
            "edad": nueva_cita.edad,
            "manzana": nueva_cita.manzana,
            "lote": nueva_cita.lote,
            "sector": nueva_cita.sector,
            "asuntos": json.loads(nueva_cita.asuntos) if nueva_cita.asuntos else [],
            "fechaVisita": nueva_cita.fechaVisita,
            "horaVisita": nueva_cita.horaVisita,
            "programador": nueva_cita.programador,
            "fechaCreacion": nueva_cita.fechaCreacion
        }
    }), 201

# 🔹 Eliminar una cita
@app.route("/api/citas/<int:cita_id>", methods=["DELETE"])
def delete_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    db.session.delete(cita)
    db.session.commit()
    return jsonify({"message": "Cita eliminada con éxito"})

# 🔹 Editar una cita existente
@app.route("/api/citas/<int:cita_id>", methods=["PUT"])
def update_cita(cita_id):
    cita = Cita.query.get_or_404(cita_id)
    data = request.get_json()
    
    # Actualizar los campos con los datos del JSON
    cita.numExpediente = data.get("numExpediente", cita.numExpediente)
    cita.fechaIngreso = data.get("fechaIngreso", cita.fechaIngreso)
    cita.nombreAdmin = data.get("nombreAdmin", cita.nombreAdmin)
    cita.dni = data.get("dni", cita.dni)
    cita.edad = data.get("edad", cita.edad)
    cita.manzana = data.get("manzana", cita.manzana)
    cita.lote = data.get("lote", cita.lote)
    cita.sector = data.get("sector", cita.sector)
    cita.asuntos = json.dumps(data.get("asuntos", [])) # Guardamos como JSON string
    cita.fechaVisita = data.get("fechaVisita", cita.fechaVisita)
    cita.horaVisita = data.get("horaVisita", cita.horaVisita)
    cita.programador = data.get("programador", cita.programador)

    db.session.commit()
    
    return jsonify({
        "message": "Cita actualizada con éxito",
        "cita": {
            "id": cita.id,
            "numExpediente": cita.numExpediente,
            "fechaIngreso": cita.fechaIngreso,
            "nombreAdmin": cita.nombreAdmin,
            "dni": cita.dni,
            "edad": cita.edad,
            "manzana": cita.manzana,
            "lote": cita.lote,
            "sector": cita.sector,
            "asuntos": json.loads(cita.asuntos) if cita.asuntos else [],
            "fechaVisita": cita.fechaVisita,
            "horaVisita": cita.horaVisita,
            "programador": cita.programador,
            "fechaCreacion": cita.fechaCreacion
        }
    })

# ------------------------
# MAIN
# ------------------------
# Este bloque es necesario para que la aplicación se ejecute correctamente.
if __name__ == "__main__":
    app.run(debug=True)
