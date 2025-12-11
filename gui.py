# gui.py
import tkinter as tk
import os
from tkinter import ttk, messagebox, simpledialog
from operations import ver_cliente_con_saldo, registrar_factura, registrar_pago
from models import crear_cliente




class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cuentas Corrientes - Ferretería")
        self.geometry("900x700")
        self.create_widgets()
        self.cargar_clientes()

    def create_widgets(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(fill='x', padx=8, pady=6)

        ttk.Button(toolbar, text="Nuevo Cliente", command=self.nuevo_cliente).pack(side='left')
        ttk.Button(toolbar, text="Refrescar", command=self.cargar_clientes).pack(side='left')

        columns = ("id","nombre","telefono","saldo")
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column("nombre", width=300)
        self.tree.pack(fill='both', expand=True, padx=8, pady=8)
        self.tree.bind("<Double-1>", self.on_double_click)

    def cargar_clientes(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        for c in ver_cliente_con_saldo():
            self.tree.insert("", "end", values=(c['id'], c['nombre'], c.get('telefono') or "", "{:.2f}".format(c['saldo'])))

    def nuevo_cliente(self):
        nombre = simpledialog.askstring("Nuevo cliente", "Nombre del cliente:", parent=self)
        if not nombre:
            return
        telefono = simpledialog.askstring("Nuevo cliente", "Teléfono (opcional):", parent=self)
        crear_cliente(nombre, telefono)
        self.cargar_clientes()

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        vals = self.tree.item(item, 'values')
        cliente_id, nombre = vals[0], vals[1]
        self.abrir_detalle_cliente(int(cliente_id), nombre)

    def abrir_detalle_cliente(self, cliente_id, nombre):
        dlg = tk.Toplevel(self)
        dlg.title(f"Cliente - {nombre}")
        dlg.geometry("500x400")
        ttk.Label(dlg, text=f"Cliente: {nombre} (ID {cliente_id})").pack(pady=6)

        frame = ttk.Frame(dlg)
        frame.pack(fill='x', padx=18, pady=18)
        ttk.Button(frame, text="Agregar Factura", command=lambda: self.agregar_movimiento_popup(cliente_id, "FACTURA", dlg)).pack(side='left', padx=4)
        ttk.Button(frame, text="Registrar Pago", command=lambda: self.agregar_movimiento_popup(cliente_id, "PAGO", dlg)).pack(side='left', padx=4)
        ttk.Button(frame, text="Imprimir Recibo",command=lambda: self.imprimir_recibo_cliente(cliente_id, nombre, dlg)
                    ).pack(side='left', padx=4)

        


        # movimientos
        tree = ttk.Treeview(dlg, columns=("fecha","tipo","desc","monto"), show='headings')
        for h in ("fecha","tipo","desc","monto"):
            tree.heading(h, text=h.capitalize())
        tree.pack(fill='both', expand=True, padx=8, pady=8)
        # cargar movimientos
        from models import obtener_movimientos, calcular_saldo
        for m in obtener_movimientos(cliente_id):
            tree.insert("", "end", values=(m['fecha'], m['tipo'], m['descripcion'] or "", "{:.2f}".format(m['monto'])))
        saldo = calcular_saldo(cliente_id)
        ttk.Label(dlg, text=f"Saldo: {saldo:.2f}").pack(pady=18)

    def agregar_movimiento_popup(self, cliente_id, tipo, parent):
        from tkinter.simpledialog import askfloat, askstring
        monto = askfloat(tipo, "Monto:", parent=parent)
        if monto is None:
            return
        desc = askstring(tipo, "Descripción (opcional):", parent=parent)
        if tipo == "FACTURA":
            registrar_factura(cliente_id, monto, desc)
        else:
            registrar_pago(cliente_id, monto, desc)
        messagebox.showinfo("OK", f"{tipo} registrada.")
        self.cargar_clientes()
        
    def imprimir_recibo_cliente(self, cliente_id, nombre, dlg):
        from operations import imprimir_recibo, obtener_movimientos_con_saldo
        import tempfile

        # Obtener movimientos y saldo
        movimientos, saldo = obtener_movimientos_con_saldo(cliente_id)

        # Generar texto del recibo
        recibo_texto = imprimir_recibo(nombre, movimientos, saldo)

        # Mostrarlo antes de imprimir
        messagebox.showinfo("Recibo generado", recibo_texto)

        try:
            # Crear archivo temporal .txt
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
                tmp.write(recibo_texto)
                tmp_path = tmp.name

            # Enviar a impresora POS en Windows
            os.system(f'notepad /p "{tmp_path}"')

            messagebox.showinfo("Impresión", "Recibo enviado a la impresora.")

        except Exception as e:
            messagebox.showerror("Error al imprimir", str(e))

        dlg.destroy()
