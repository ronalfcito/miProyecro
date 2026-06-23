import os
import time
from flask import Flask, jsonify, render_template_string
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Variables de entorno
APP_NAME = os.getenv("APP_NAME", "Sistema DevOps")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "devops_db")
DB_USER = os.getenv("DB_USER", "devops_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "devops_password")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def init_db():
    for attempt in range(15):
        try:
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS productos (
                        id SERIAL PRIMARY KEY,
                        nombre VARCHAR(100) NOT NULL,
                        precio NUMERIC(10,2) NOT NULL,
                        stock INTEGER NOT NULL DEFAULT 0
                    )
                """)
                cur.execute("""
                    INSERT INTO productos (nombre, precio, stock)
                    SELECT 'Producto de ejemplo', 19.99, 10
                    WHERE NOT EXISTS (SELECT 1 FROM productos)
                """)
            conn.commit()
            conn.close()
            return
        except Exception:
            if attempt == 14:
                raise
            time.sleep(2)


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

    html_template = """
    <!DOCTYPE html>
    <html>
    <head><title>{{ app_name }}</title></head>
    <body style="font-family: Arial, sans-serif; margin: 50px;">
        <h1>Examen Práctico DevOps</h1>
        <p><strong>Nombre de la Aplicación:</strong> {{ app_name }}</p>
        <p><strong>Versión Actual:</strong> {{ app_version }}</p>
        <p><strong>Estado de conexión con PostgreSQL:</strong> {{ status }}</p>
        <br>
        <a href="/productos" style="padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px;">Visualizar todos los productos</a>
    </body>
    </html>
    """
    return render_template_string(html_template, app_name=APP_NAME, app_version=APP_VERSION, status=status)

@app.route('/productos')
def listar_productos():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Va directo a consultar la tabla que creaste en pgAdmin
        cur.execute("SELECT id, nombre, precio, stock FROM productos;")
        productos = cur.fetchall()
        
        cur.close()
        conn.close()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)