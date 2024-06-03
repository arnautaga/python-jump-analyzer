import tkinter as tk
from tkinter import filedialog
import darkdetect
import numpy as np

from redes import Redes
from analisis import Analisis


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.arqred = Redes()
        self.analisis = Analisis()
        self.logeado = False
        self.file_path = ""
        self.masa_entry = tk.Entry
        self.masa = 0

        self.tema = "Light"

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

        tk.Label(self.root, text="Iniciar sesión", font=('bold', 18)).pack(pady=8)

        tk.Label(self.root, text="Nombre de usuario:").pack(pady=5)
        self.usuario_entry = tk.Entry(self.root).pack(pady=5)

        tk.Label(self.root, text="Contraseña:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*").pack(pady=5)

        tk.Button(self.root, text="Iniciar sesión", command=self.procesar_inicio_sesion, width=13).pack(pady=12)

        if not bool:
            label_error = tk.Label(self.root,
                                   text="Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo.", fg="red")
            label_error.pack(pady=5)

    def procesar_inicio_sesion(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()
        self.arqred.iniciar_sesion(usuario, password, self)

    def analizar_archivo(self):
        datos = self.analisis.get_datos_analisis(self.file_path, self.masa)

        self.limpiar_ventana()

        datos_frame, graficas_frame = self.crear_pantalla_analisis()

        tk.Label(datos_frame, text='La gravedad estimada del móvil es: {0:.2f} m/s²'.format(datos["a_grav"])).pack(
            pady=(30, 0))
        tk.Label(datos_frame,
                 text='La aceleracion maxima durante el vuelo es: {0:.2f} m/s²'.format(datos["a_max"])).pack(pady=5)
        tk.Label(datos_frame, text='La fuerza maxima durante el vuelo es: {0:.2f} N'.format(datos["f_max"])).pack(
            pady=5)
        tk.Label(datos_frame,
                 text='La velocidad maxima durante su vuelo es: {0:.2f} m/s.'.format(datos["v_max"])).pack(pady=5)
        tk.Label(datos_frame,
                 text='La potencia maxima durante el vuelo es: {0:.2f} W'.format(datos["p_max"])).pack(pady=5)
        tk.Label(datos_frame, text='La altura del salto es: {0:.2f} metros.'.format(datos["alt_salto"])).pack(
            pady=5)
        tk.Label(datos_frame, text='La duración del vuelo es: {0:.2f} segundos.'.format(datos["t_vuelo"])).pack(
            pady=5)

        tk.Button(graficas_frame, text='Mostrar gráfica de aceleración',
                  command=lambda: self.analisis.grafica_aceleracion(self.file_path, self.masa), height=2,
                  width=30).pack(pady=(20, 10))
        tk.Button(graficas_frame, text='Mostrar gráfica de fuerza',
                  command=lambda: self.analisis.grafica_fuerza(self.file_path, self.masa), height=2, width=30).pack(
            pady=10)
        tk.Button(graficas_frame, text='Mostrar gráfica de velocidad',
                  command=lambda: self.analisis.grafica_velocidad(self.file_path, self.masa), height=2, width=30).pack(
            pady=10)
        tk.Button(graficas_frame, text='Mostrar gráfica de potencia',
                  command=lambda: self.analisis.grafica_potencia(self.file_path, self.masa), height=2, width=30).pack(
            pady=10)

    def open_file(self):
        if not self.masa_entry.get() == '':
            if not int(float(self.masa_entry.get())) <= 0:
                # Abre el selector de fichero y obtiene la ruta del fichero seleccionado
                self.file_path = filedialog.askopenfilename(
                    title="Seleccionar fichero",
                    filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
                )

                if self.file_path:
                    self.masa = int(float(self.masa_entry.get()))
                    self.analizar_archivo()
            else:
                tk.messagebox.showerror('Error', 'Valor de masa inválido.')
        else:
            tk.messagebox.showerror('Error', 'Por favor, introduzca la masa.')

    def cambiar_tema(self, tema):
        self.tema = tema
        if self.tema == 'Dark':
            self.root.configure(background='gray15')
        elif self.tema == 'Light':
            self.root.configure(background='light gray')

    def pantalla_ajustes(self):
        self.limpiar_ventana()

        tk.Label(self.root, text='Temas', font='bold').pack(pady=(25, 15))

        tk.Button(self.root, text="Tema claro", command= lambda: self.cambiar_tema('Light'), height=2, width=25).pack(pady=(55, 20))
        tk.Button(self.root, text="Tema oscuro", command= lambda: self.cambiar_tema('Dark'), height=2, width=25).pack(pady=20)
        tk.Button(self.root, text="Tema del sistema", command= lambda: self.cambiar_tema(darkdetect.theme()), height=2, width=25).pack(pady=20)

    def pantalla_reglas(self):
        self.limpiar_ventana()
        tk.Label(self.root, text='¿Cómo se debe realizar el salto?', font='bold').pack(pady=(25, 15))
        tk.Label

        tk.Label(self.root,
                 text=''
        'Para realizar un salto correctamente, sigue estos pasos: \n\n\n1. Sujeta firmemente el móvil a la pelvis con una banda elástica, preferiblemente en un lateral,\nentre la cadera y la cresta ilíaca.\n\n2. Desde una posición agachada, cruza los brazos sobre el pecho o apóyalos en la cintura,\ncuidando de no tocar el móvil.\n\n3. Configura el dispositivo para que emita un aviso de 5 segundos y espere otros\n5 segundos para la medición (configuración predeterminada).\n\n4. Tras el aviso, espera al menos dos segundos en reposo para calibrar la medida. Luego, salta\nverticalmente con toda tu fuerza.\n\n5. Al caer, permanece erguido y quieto hasta oír el siguiente aviso.\n\n6. Finalmente, envía los datos obtenidos por correo o cualquier otro método, asegurándose de\nidentificar claramente la medición.', font=('Arial', 12)).pack(pady=10)

    def crear_pantalla_analisis(self):
        self.limpiar_ventana()

        datos_frame = tk.Frame(self.root)
        graficas_frame = tk.Frame(self.root)
        datos_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        graficas_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(datos_frame, text='Datos del salto', font='bold').pack(pady=5)
        tk.Label(graficas_frame, text='Gráficas', font='bold').pack(pady=5)

        tk.Label(datos_frame, text='Introduzca la masa en kilogramos:').pack(pady=5)
        self.masa_entry = tk.Entry(datos_frame)
        self.masa_entry.pack(pady=5)

        tk.Label(datos_frame, text='Seleccione un archivo:').pack(pady=5)
        tk.Button(datos_frame, text='Seleccionar', command=lambda: self.open_file()).pack(pady=5)

        return datos_frame, graficas_frame

    def crear_menu_base(self):
        tk.Label(self.root, text="MENÚ", font=('bold', 30)).pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.X, expand=False, pady=65)

        tk.Button(frame, text="Ajustes", command=self.pantalla_ajustes, height=2, width=15).grid(row=0, column=1, padx=125)
        tk.Button(frame, text="Reglas", command=self.pantalla_reglas, height=2, width=15).grid(row=0, column=2, padx=125)

        tk.Button(self.root, text="Analizar salto", command=lambda: self.crear_pantalla_analisis(), height=3,
                  width=30).pack(pady=10)

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

        self.crear_menu_base()

        if logeado:
            tk.Button(self.root, text="Clasificación de saltos", command=self.open_file, height=3, width=30).pack(
                pady=10)
            tk.Button(self.root, text="Enviar datos de salto", command=self.open_file, height=3, width=30).pack(pady=10)
            tk.Button(self.root, text="Cerrar sesión", command=self.open_file, height=2, width=15).pack(pady=40)
        else:
            tk.Button(self.root, text="Iniciar sesión", command=lambda: self.ventana_iniciar_sesion(True), height=2,
                      width=15).pack(pady=40)
