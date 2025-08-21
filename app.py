from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Crear la base de datos si no existe
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            fecha TEXT,
            hora TEXT,
            descripcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha = request.form['fecha']
        hora = request.form['hora']
        descripcion = request.form['descripcion']

        c.execute('INSERT INTO citas (nombre, fecha, hora, descripcion) VALUES (?, ?, ?, ?)',
                  (nombre, fecha, hora, descripcion))
        conn.commit()
        return redirect('/')

    c.execute('SELECT * FROM citas')
    citas = c.fetchall()
    conn.close()
    return render_template('index.html', citas=citas)

if __name__ == '__main__':
    app.run(debug=True)
