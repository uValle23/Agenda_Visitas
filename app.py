import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import sys

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

class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(100), nullable=False)
    hora = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha = request.form['fecha']
        hora = request.form['hora']
        descripcion = request.form['descripcion']

        nueva_cita = Cita(nombre=nombre, fecha=fecha, hora=hora, descripcion=descripcion)
        db.session.add(nueva_cita)
        db.session.commit()
        return redirect('/')

    citas = Cita.query.all()
    return render_template('index.html', citas=citas)

if __name__ == '__main__':
    app.run(debug=True)
