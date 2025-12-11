# models.py
from db import get_connection
from decimal import Decimal

def crear_cliente(nombre, telefono=None, direccion=None, email=None):
    conn = get_connection()
    cur = conn.cursor()
    sql = "INSERT INTO clientes (nombre, telefono, direccion, email) VALUES (%s,%s,%s,%s)"
    cur.execute(sql, (nombre, telefono, direccion, email))
    conn.commit()
    cliente_id = cur.lastrowid
    cur.close()
    conn.close()
    return cliente_id

def obtener_clientes():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM clientes ORDER BY nombre")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def agregar_movimiento(cliente_id, tipo, monto, descripcion=None, documento=None):
    # monto: positivo para facturas, positivo para pagos (luego en cálculo se resta según tipo)
    conn = get_connection()
    cur = conn.cursor()
    sql = """INSERT INTO movimientos (cliente_id, tipo, descripcion, monto, documento)
             VALUES (%s,%s,%s,%s,%s)"""
    cur.execute(sql, (cliente_id, tipo, descripcion, monto, documento))
    conn.commit()
    mid = cur.lastrowid
    cur.close()
    conn.close()
    return mid

def obtener_movimientos(cliente_id):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM movimientos WHERE cliente_id = %s ORDER BY fecha", (cliente_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def calcular_saldo(cliente_id):
    """
    Convención:
     - FACTURA: cliente debe (monto aumenta saldo)
     - NOTA_DEBITO: aumenta saldo
     - PAGO: reduce saldo
     - NOTA_CREDITO: reduce saldo
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT tipo, SUM(monto) FROM movimientos WHERE cliente_id=%s GROUP BY tipo", (cliente_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    totals = {r[0]: Decimal(r[1] or 0) for r in rows}
    saldo = Decimal('0.00')
    saldo += totals.get('FACTURA', Decimal('0.00'))
    saldo += totals.get('NOTA_DEBITO', Decimal('0.00'))
    saldo -= totals.get('PAGO', Decimal('0.00'))
    saldo -= totals.get('NOTA_CREDITO', Decimal('0.00'))
    return float(saldo)
