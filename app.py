from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Conexión a PostgreSQL desde Render o SQLite si es local
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la tabla
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.String(100), nullable=False)
    hora = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

# Crear las tablas si no existen
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
