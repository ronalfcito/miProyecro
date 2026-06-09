import os
from flask import Flask, jsonify, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Variables de entorno
APP_NAME = os.getenv("APP_NAME", "App DevOps")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "devops_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_db():
    """Inicializa la base de datos creando la tabla e insertando 5 registros."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Crear tabla
        cur.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                precio NUMERIC(10, 2) NOT NULL,
                stock INT NOT NULL
            );
        """)
        
        # Verificar si ya existen registros
        cur.execute("SELECT COUNT(*) FROM productos;")
        if cur.fetchone()[0] == 0:
            productos_semilla = [
                ('Laptop', 1200.50, 10),
                ('Mouse', 25.00, 50),
                ('Teclado', 45.00, 30),
                ('Monitor', 300.00, 15),
                ('Audífonos', 75.20, 25)
            ]
            cur.executemany(
                "INSERT INTO productos (nombre, precio, stock) VALUES (%s, %s, %s);",
                productos_semilla
            )
        
        conn.commit()
        cur.close()
        conn.close()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")

# Inicializar DB al arrancar la app
init_db()

@app.route('/')
def index():
    status = "Desconectado"
    try:
        conn = get_db_connection()
        status = "Conectado exitosamente"
        conn.close()
    except Exception as e:
        status = f"Error de conexión: {str(e)}"

    # Template HTML integrado para la página principal
    html_template = """
    <!... html ...>
    <html>
    <head><title>{{ app_name }}</title></head>
    <body style="font-family: Arial, sans-serif; margin: 40px;">
        <h1>Examen Práctico DevOps</h1>
        <p><strong>Aplicación:</strong> {{ app_name }}</p>
        <p><strong>Versión:</strong> {{ app_version }}</p>
        <p><strong>Estado de conexión a PostgreSQL:</strong> {{ status }}</p>
        <br>
        <a href="/productos" style="padding: 10px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Ver Productos</a>
    </body>
    </html>
    """
    return render_template_string(html_template, app_name=APP_NAME, app_version=APP_VERSION, status=status)

@app.route('/productos')
def get_productos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nombre, precio, stock FROM productos;")
        productos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)