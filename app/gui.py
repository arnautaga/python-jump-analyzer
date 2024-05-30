import tkinter as tk
from tkinter import filedialog
import darkdetect
import numpy as np

from redes import Redes


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.arqred = Redes()
        self.logeado = False
        self.file_path = ""

        self.root.title("POLI[LOCURA]")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        self.crear_ventana_principal()
        self.root.mainloop()

    def crear_ventana_principal(self):
        self.limpiar_ventana()

        self.bienvenida_frame = tk.Frame(self.root)
        self.bienvenida_frame.pack()

        imagen_bienvenida = tk.PhotoImage(file="logo.png")
        label_imagen = tk.Label(self.bienvenida_frame, image=imagen_bienvenida)
        label_imagen.image = imagen_bienvenida
        label_imagen.pack()

        boton_invitado = tk.Button(self.bienvenida_frame, text="Acceder como invitado",
                                   command=self.acceder_como_invitado)
        boton_invitado.pack(pady=5)

        boton_iniciar_sesion = tk.Button(self.bienvenida_frame, text="Acceder como usuario registrado",
                                         command=self.ventana_iniciar_sesion)
        boton_iniciar_sesion.pack(pady=5)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def acceder_como_invitado(self):
        self.menu(False)

    def ventana_iniciar_sesion(self, bool=True):
        self.limpiar_ventana()

        self.inicio_sesion_frame = tk.Frame(self.root)
        self.inicio_sesion_frame.pack()

        label_login = tk.Label(self.inicio_sesion_frame, text="Nombre de usuario:")
        label_login.pack(pady=5)
        self.usuario_entry = tk.Entry(self.inicio_sesion_frame)
        self.usuario_entry.pack(pady=5)

        label_password = tk.Label(self.inicio_sesion_frame, text="Contraseña:")
        label_password.pack(pady=5)
        self.password_entry = tk.Entry(self.inicio_sesion_frame, show="*")
        self.password_entry.pack(pady=5)

        boton_iniciar = tk.Button(self.inicio_sesion_frame, text="Iniciar sesión", command=self.procesar_inicio_sesion)
        boton_iniciar.pack(pady=5)

        if not bool:
            label_error = tk.Label(self.inicio_sesion_frame,
                                   text="Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo.", fg="red")
            label_error.pack(pady=5)

    def procesar_inicio_sesion(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()
        self.arqred.iniciar_sesion(usuario, password, self)

    def open_file(self):
        # Abre el selector de fichero y obtiene la ruta del fichero seleccionado
        self.file_path = filedialog.askopenfilename(
            title="Seleccionar fichero",
            filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
        )

    def crear_menu_base(self):
        tk.Label(self.root, text="MENÚ", font=('bold', 30)).pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, expand=False, pady=65)

        tk.Button(frame, text="Ajustes", command=self.open_file, height=2, width=15).grid(row=0, column=1, padx=65)
        tk.Button(frame, text="Reglas", command=self.open_file, height=2, width=15).grid(row=0, column=2, padx=65)
        tk.Button(frame, text="Créditos", command=self.open_file, height=2, width=15).grid(row=0, column=3, padx=65)

        tk.Button(self.root, text="Analizar salto", command=self.open_file, height=3, width=30).pack(pady=10)

        return frame

    def crear_elementos_logeado(self, enviar_frame, leaderboard_frame):
        tk.Label(enviar_frame, text="Enviar").pack(pady=5)
        tk.Button(enviar_frame, text="Enviar", command=lambda: print("Enviar")).pack(pady=5)

        # Sección de leaderboard
        leaderboard_data = self.arqred.obtener_leaderboard()
        tk.Label(leaderboard_frame, text="Leaderboard").pack(pady=5)

        leaderboard_info = "\n".join([
            f"Usuario: {entry['nombre']}, Grupo: {entry['grupo_ProMu']}, "
            f"Altura: {entry['altura']}, Fecha: {entry['fecha']}"
            for entry in leaderboard_data])
        tk.Label(leaderboard_frame, text=leaderboard_info).pack(pady=5)

    def menu(self, logeado):
        self.logeado = logeado
        self.limpiar_ventana()

        frame = self.crear_menu_base()

        if logeado:
            tk.Button(self.root, text="Clasificación de saltos", command=self.open_file, height=3, width=30).pack(pady=10)
            tk.Button(self.root, text="Enviar datos de salto", command=self.open_file, height=3, width=30).pack(pady=10)
            tk.Button(self.root, text="Cerrar sesión", command=self.open_file, height=2, width=15).pack(pady=40)
        else:
            tk.Button(self.root, text="Iniciar sesión", command=self.open_file, height=2, width=15).pack(pady=40)
