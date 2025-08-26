import os
import sys
from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy

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
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(100), nullable=False)
    hora = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

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
    return jsonify([
        {
            "id": c.id,
            "nombre": c.nombre,
            "fecha": c.fecha,
            "hora": c.hora,
            "descripcion": c.descripcion
        } for c in citas
    ])

# 🔹 Registrar nueva cita
@app.route("/api/citas", methods=["POST"])
def add_cita():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Faltan datos"}), 400

    nueva = Cita(
        nombre=data.get("nombre", ""),
        fecha=data.get("fecha", ""),
        hora=data.get("hora", ""),
        descripcion=data.get("descripcion", "")
    )
    db.session.add(nueva)
    db.session.commit()

    return jsonify({
        "id": nueva.id,
        "nombre": nueva.nombre,
        "fecha": nueva.fecha,
        "hora": nueva.hora,
        "descripcion": nueva.descripcion
    }), 201

# ------------------------
# MAIN
# ------------------------
if __name__ == "__main__":
    app.run(debug=True)
