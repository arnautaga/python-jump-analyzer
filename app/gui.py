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

        self.usuario_entry = tk.Entry
        self.password = tk.Entry

        self.tema = "Light"
        self.temas = {"Light": {"bg": "SystemButtonFace", "fg": "black"}, "Dark": {"bg": "gray19", "fg": "ghost white"}}

        self.root.title("POLI[LOCURA]")
        self.root.geometry("750x600")
        self.root.resizable(False, False)

        self.crear_ventana_principal()
        self.root.mainloop()

    def get_color_tema(self, key):
        return self.temas[self.tema][key]

    def barra_menu(self):
        menubar = tk.Menu(self.root)
        menubar.add_command(label="Home", command=lambda: self.menu(self.logeado))
        self.root.config(menu=menubar)

    def barra_inicio(self):
        menubar = tk.Menu(self.root)
        menubar.add_command(label="Inicio", command=lambda: self.crear_ventana_principal())
        self.root.config(menu=menubar)

    def crear_ventana_principal(self):
        self.limpiar_ventana()

        self.bienvenida_frame = tk.Frame(self.root, bg=self.get_color_tema('bg'))
        self.bienvenida_frame.pack()

        imagen_bienvenida = tk.PhotoImage(file="logo.png")
        label_imagen = tk.Label(self.bienvenida_frame, image=imagen_bienvenida)
        label_imagen.image = imagen_bienvenida
        label_imagen.pack()

        boton_invitado = tk.Button(self.bienvenida_frame, text="Acceder como invitado",
                                   command=self.acceder_como_invitado, bg=self.get_color_tema('bg'),
                                   fg=self.get_color_tema('fg'))
        boton_invitado.pack(pady=5)

        boton_iniciar_sesion = tk.Button(self.bienvenida_frame, text="Acceder como usuario registrado",
                                         command=self.ventana_iniciar_sesion, bg=self.get_color_tema('bg'),
                                         fg=self.get_color_tema('fg'))
        boton_iniciar_sesion.pack(pady=5)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def acceder_como_invitado(self):
        self.menu(False)

    def procesar_inicio_sesion(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()
        self.arqred.iniciar_sesion(usuario, password, self)

    def ventana_iniciar_sesion(self, bool=True):
        self.limpiar_ventana()
        self.barra_inicio()

        tk.Label(self.root, text="Iniciar sesión", font=('bold', 18), bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=8)

        tk.Label(self.root, text="Nombre de usuario:", bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=5)
        self.usuario_entry = tk.Entry(self.root)
        self.usuario_entry.pack(pady=5)

        tk.Label(self.root, text="Contraseña:", bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        tk.Button(self.root, text="Iniciar sesión", command=self.procesar_inicio_sesion, height=2, width=15,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=20)

        if not bool:
            label_error = tk.Label(self.root, text="Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo.",
                                   bg=self.get_color_tema('bg'), fg="red", font=("bold", 12))
            label_error.pack(pady=5)

    def analizar_archivo(self):
        datos = self.analisis.get_datos_analisis(self.file_path, self.masa)

        self.limpiar_ventana()

        datos_frame, graficas_frame = self.crear_pantalla_analisis()

        tk.Label(datos_frame, text='La gravedad estimada del móvil es: {0:.2f} m/s²'.format(datos["a_grav"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=(30, 0))
        tk.Label(datos_frame, text='La aceleracion maxima durante el vuelo es: {0:.2f} m/s²'.format(datos["a_max"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Label(datos_frame, text='La fuerza maxima durante el vuelo es: {0:.2f} N'.format(datos["f_max"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Label(datos_frame, text='La velocidad maxima durante su vuelo es: {0:.2f} m/s.'.format(datos["v_max"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Label(datos_frame, text='La potencia maxima durante el vuelo es: {0:.2f} W'.format(datos["p_max"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Label(datos_frame, text='La altura del salto es: {0:.2f} metros.'.format(datos["alt_salto"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Label(datos_frame, text='La duración del vuelo es: {0:.2f} segundos.'.format(datos["t_vuelo"]),
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)

        tk.Button(graficas_frame, text='Mostrar gráfica de aceleración',
                  command=lambda: self.analisis.grafica_aceleracion(self.file_path, self.masa), height=2, width=30,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=(20, 10))
        tk.Button(graficas_frame, text='Mostrar gráfica de fuerza',
                  command=lambda: self.analisis.grafica_fuerza(self.file_path, self.masa), height=2, width=30,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)
        tk.Button(graficas_frame, text='Mostrar gráfica de velocidad',
                  command=lambda: self.analisis.grafica_velocidad(self.file_path, self.masa), height=2, width=30,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)
        tk.Button(graficas_frame, text='Mostrar gráfica de potencia',
                  command=lambda: self.analisis.grafica_potencia(self.file_path, self.masa), height=2, width=30,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)

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
        if tema == 'Dark':
            self.root.configure(background='gray15')
        elif self.tema == 'Light':
            self.root.configure(background='SystemButtonFace')

        self.pantalla_ajustes()

    def pantalla_ajustes(self):
        self.limpiar_ventana()
        self.barra_menu()

        tk.Label(self.root, text='Temas', font='bold', bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(25, 15))

        tk.Button(self.root, text="Tema claro", command=lambda: self.cambiar_tema('Light'), height=2, width=25,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(55, 20))
        tk.Button(self.root, text="Tema oscuro", command=lambda: self.cambiar_tema('Dark'), height=2, width=25,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=20)
        tk.Button(self.root, text="Tema del sistema",
                  command=lambda: self.cambiar_tema(darkdetect.theme()), bg=self.get_color_tema('bg'),
                  fg=self.get_color_tema('fg'), height=2, width=25).pack(pady=20)

    def pantalla_reglas(self):
        self.limpiar_ventana()
        self.barra_menu()

        tk.Label(self.root, text='¿Cómo se debe realizar el salto?', font='bold', bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=(25, 15))
        tk.Label(self.root,
                 text='Para realizar un salto correctamente, sigue estos pasos: \n\n\n1. Sujeta firmemente el móvil a la pelvis con una banda elástica, preferiblemente en un lateral,\nentre la cadera y la cresta ilíaca.\n\n2. Desde una posición agachada, cruza los brazos sobre el pecho o apóyalos en la cintura,\ncuidando de no tocar el móvil.\n\n3. Configura el dispositivo para que emita un aviso de 5 segundos y espere otros\n5 segundos para la medición (configuración predeterminada).\n\n4. Tras el aviso, espera al menos dos segundos en reposo para calibrar la medida. Luego, salta\nverticalmente con toda tu fuerza.\n\n5. Al caer, permanece erguido y quieto hasta oír el siguiente aviso.\n\n6. Finalmente, envía los datos obtenidos por correo o cualquier otro método, asegurándose de\nidentificar claramente la medición.',
                 font=('Arial', 12), bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)

    def crear_pantalla_analisis(self):
        self.limpiar_ventana()
        self.barra_menu()

        datos_frame = tk.Frame(self.root, bg=self.get_color_tema('bg'))
        graficas_frame = tk.Frame(self.root, bg=self.get_color_tema('bg'))
        datos_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        graficas_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)

        tk.Label(datos_frame, text='Datos del salto', font='bold', bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Label(graficas_frame, text='Gráficas', font='bold', bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=5)

        tk.Label(datos_frame, text='Introduzca la masa en kilogramos:', bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=5)
        self.masa_entry = tk.Entry(datos_frame)
        self.masa_entry.pack(pady=5)

        tk.Label(datos_frame, text='Seleccione un archivo:', bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=5)
        tk.Button(datos_frame, text='Seleccionar', command=lambda: self.open_file(), bg=self.get_color_tema('bg'),
                  fg=self.get_color_tema('fg')).pack(pady=5)

        return datos_frame, graficas_frame

    def cargar_ranking(self):
        leaderboard_data = self.arqred.obtener_leaderboard()

        total_rows = len(leaderboard_data)
        total_columns = len(leaderboard_data[0])

        frame = tk.Frame(self.root)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        for i in range(total_rows):
            for j in range(total_columns):
                if i == 0:
                    e = tk.Entry(frame, width=12, font=('Arial', 15, "bold"))
                elif i > 0 and i <= 3:
                    e = tk.Entry(frame, width=12, font=('Arial', 14, "bold"))
                else:
                    e = tk.Entry(frame, width=12, font=('Arial', 14))

                e.grid(row=i, column=j)
                e.insert(tk.END, leaderboard_data[i][j])
                e.config(state="disabled")

    def crear_pantalla_ranking(self):
        self.limpiar_ventana()
        self.barra_menu()

        leaderboard_text = tk.Label(self.root, text="Leaderboard", font="bold", bg=self.get_color_tema('bg'),
                                    fg=self.get_color_tema('fg'))
        leaderboard_text.pack(pady=5)

        tk.Label(self.root, text="Cargar datos del leaderboard:\n(esta acción puede tardar un poco)",
                 bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)
        tk.Button(self.root, text="Cargar", command=lambda: self.cargar_ranking(), height=2, width=10,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(0, 10))

    def enviar_datos(self, nombre, grupo, altura, fecha, status_text, data_text):
        if nombre and grupo and altura and fecha:
            res = self.arqred.enviar_salto(nombre, grupo, altura, fecha)

            if res.startswith("200"):
                status_text.config(text="Datos enviados. ¡Estás en el top 10!")
                data_text.config(text=f"| {nombre:<10} | {grupo:^11} | {altura:^6} | {fecha:^10} |")
            elif res.startswith("201"):
                status_text.config(text="Datos enviados. Lo sentimos, no estás en el top 10.")
                data_text.config(text=f"| {nombre:<10} | {grupo:^11} | {altura:^6} | {fecha:^10} |")
            else:
                status_text.config(text="Ha ocurrido un error.")
        else:
            tk.messagebox.showerror('Error', 'Faltan campos por rellenar.')

    def crear_pantalla_envio(self):
        self.limpiar_ventana()
        self.barra_menu()

        tk.Label(self.root, text="Enviar datos del salto", font="bold", bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=5)

        tk.Label(self.root, text="Nombre:", bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(20, 5))
        nombre_entry = tk.Entry(self.root)
        nombre_entry.pack(pady=5)

        tk.Label(self.root, text="Grupo:", bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(10, 5))
        grupo_entry = tk.Entry(self.root)
        grupo_entry.pack(pady=5)

        tk.Label(self.root, text="Altura", bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(10, 5))
        altura_entry = tk.Entry(self.root)
        altura_entry.pack(pady=5)

        tk.Label(self.root, text="Fecha:", bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(
            pady=(10, 5))
        fecha = self.arqred.formato_fecha()
        tk.Label(self.root, text=fecha, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=5)

        status_text = tk.Label(self.root, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg'))
        data_text = tk.Label(self.root, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg'))

        tk.Button(self.root, text="Enviar",
                  command=lambda: self.enviar_datos(nombre_entry.get(), grupo_entry.get(), altura_entry.get(), fecha,
                                                    status_text, data_text),
                  height=2, width=15, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=25)

        status_text.pack(pady=(10, 5))
        data_text.pack()

    def crear_menu_base(self):
        tk.Label(self.root, text="MENÚ", font=('bold', 30), bg=self.get_color_tema('bg'),
                 fg=self.get_color_tema('fg')).pack(pady=5)

        frame = tk.Frame(self.root, bg=self.get_color_tema('bg'))
        frame.pack(fill=tk.X, expand=False, pady=65)

        tk.Button(frame, text="Ajustes", command=self.pantalla_ajustes, height=2, width=15,
                  bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).grid(row=0, column=1, padx=125)
        tk.Button(frame, text="Reglas", command=self.pantalla_reglas, height=2, width=15, bg=self.get_color_tema('bg'),
                  fg=self.get_color_tema('fg')).grid(row=0, column=2, padx=125)
        tk.Button(self.root, text="Analizar salto", command=lambda: self.crear_pantalla_analisis(), height=3,
                  width=30, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)

    def cerrar_sesion(self):
        answer = tk.messagebox.askokcancel("Cerrar sesión", "¿Desea cerrar sesión?")
        if answer:
            self.arqred.cerrar_sesion()
            self.crear_ventana_principal()

    def menu(self, logeado):
        self.logeado = logeado
        self.limpiar_ventana()
        self.crear_menu_base()

        if logeado:
            tk.Button(self.root, text="Clasificación de saltos", command=lambda: self.crear_pantalla_ranking(),
                      height=3, width=30, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)
            tk.Button(self.root, text="Enviar datos de salto", command=lambda: self.crear_pantalla_envio(), height=3,
                      width=30, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=10)
            tk.Button(self.root, text="Cerrar sesión", command=lambda: self.cerrar_sesion(), height=2, width=15,
                      bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=40)
        else:
            tk.Button(self.root, text="Iniciar sesión", command=lambda: self.ventana_iniciar_sesion(True), height=2,
                      width=15, bg=self.get_color_tema('bg'), fg=self.get_color_tema('fg')).pack(pady=40)
