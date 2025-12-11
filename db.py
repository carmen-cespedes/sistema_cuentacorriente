# db.py
import mysql.connector
from mysql.connector import Error
import os

def get_config():
    # configura aquí las credenciales: en producción usa variables de entorno
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASS", "rootroot"),
        "database": os.getenv("DB_NAME", "ferreteria_cc"),
        "port": int(os.getenv("DB_PORT", "3306"))
    }

def get_connection():
    cfg = get_config()
    try:
        conn = mysql.connector.connect(**cfg)
        return conn
    except Error as e:
        raise RuntimeError(f"No se pudo conectar a MySQL: {e}")
