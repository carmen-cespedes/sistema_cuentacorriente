# operations.py
from models import (
    crear_cliente,
    obtener_clientes,
    agregar_movimiento,
    obtener_movimientos,
    calcular_saldo
)
from datetime import datetime

# ----------------------------
# Funciones de registro
# ----------------------------

def registrar_factura(cliente_id, monto, descripcion="", documento=None):
    """Registra una factura para el cliente."""
    try:
        return agregar_movimiento(cliente_id, "FACTURA", monto, descripcion, documento)
    except Exception as e:
        print(f"Error al registrar factura: {e}")
        return None

def registrar_pago(cliente_id, monto, descripcion="", documento=None):
    """Registra un pago para el cliente."""
    try:
        return agregar_movimiento(cliente_id, "PAGO", monto, descripcion, documento)
    except Exception as e:
        print(f"Error al registrar pago: {e}")
        return None

def registrar_nota_credito(cliente_id, monto, descripcion="", documento=None):
    """Registra una nota de crédito (reduce saldo)."""
    try:
        return agregar_movimiento(cliente_id, "NOTA_CREDITO", monto, descripcion, documento)
    except Exception as e:
        print(f"Error al registrar nota de crédito: {e}")
        return None

def registrar_nota_debito(cliente_id, monto, descripcion="", documento=None):
    """Registra una nota de débito (aumenta saldo)."""
    try:
        return agregar_movimiento(cliente_id, "NOTA_DEBITO", monto, descripcion, documento)
    except Exception as e:
        print(f"Error al registrar nota de débito: {e}")
        return None

# ----------------------------
# Funciones de consulta
# ----------------------------

def ver_cliente_con_saldo():
    """Devuelve lista de clientes con saldo actualizado."""
    lista = []
    for c in obtener_clientes():
        saldo = calcular_saldo(c['id'])
        lista.append({**c, "saldo": saldo})
    return lista

def ver_cliente_con_saldo_ordenado(desc=False):
    """Lista clientes con saldo ordenado."""
    lista = ver_cliente_con_saldo()
    return sorted(lista, key=lambda x: x['saldo'], reverse=desc)

def obtener_movimientos_con_saldo(cliente_id):
    """Devuelve (lista_movimientos, saldo_final)."""
    movimientos = obtener_movimientos(cliente_id)
    saldo = 0
    lista = []

    for m in movimientos:
        tipo = m['tipo']
        monto = float(m['monto'])

        if tipo in ('FACTURA', 'NOTA_DEBITO'):
            saldo += monto
        else:  # PAGO, NOTA_CREDITO
            saldo -= monto

        m['saldo_acumulado'] = saldo

        # Asegurar fecha como datetime
        fecha = m['fecha']
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
        m['fecha'] = fecha

        lista.append(m)

    return lista, saldo


def imprimir_recibo(cliente, movimientos, saldo_final):
    """
    Imprime un recibo en impresora térmica POS usando python-escpos.
    cliente: dict con datos del cliente
    movimientos: lista con movimientos, incluyendo fecha, tipo, monto, descripcion.
    """
    try:
        from escpos.printer import Usb

        # ⚠️ AJUSTAR vendor_id y product_id según tu impresora real
        p = Usb(0x04b8, 0x0202)

        # Encabezado
        p.set(align='center', bold=True)
        p.text("FERRETERÍA EL CAMPO\n")
        p.text("CUENTA CORRIENTE\n")
        p.text("------------------------------\n")

        # Datos del cliente
        p.set(align='left', bold=False)
        p.text(f"Cliente: {cliente['nombre']}\n")
        if cliente.get("telefono"):
            p.text(f"Tel: {cliente['telefono']}\n")
        p.text("------------------------------\n")

        # Movimientos
        for m in movimientos:
            fecha = m['fecha'].strftime("%d/%m/%Y %H:%M")
            tipo = m['tipo']
            descripcion = m.get("descripcion", "")
            monto = float(m['monto'])

            p.text(f"{fecha}\n")
            p.text(f"{tipo} - {descripcion}\n")
            p.text(f"Monto: ${monto:.2f}\n")
            p.text("------------------------------\n")

        # Saldo final
        p.set(bold=True)
        p.text(f"SALDO FINAL: ${saldo_final:.2f}\n")
        p.set(bold=False)

        p.text("\nGracias por su compra!\n\n")
        p.cut()

    except Exception as e:
        print(f"[ERROR IMPRESORA POS] {e}")
        raise e

