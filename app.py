import tkinter as tk
from tkinter import filedialog
import socket
import json
import datetime
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid


class ARQRED:
    def __init__(self):
        self.dir_socket_servidor = ("158.42.188.200", 64010)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def iniciar_sesion(self, username, password, gui):
        ip = self.obtener_ip()
        if ip:
            try:
                if not self.sock._closed:
                    self.sock.close()  # Cerrar conexión existente si está abierta
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crear un nuevo socket
                self.sock.connect(self.dir_socket_servidor)
                self.sock.send(("HELLO " + ip + "\r\n").encode())
                data = self.sock.recv(1024).decode()
                if "200" in data:
                    self.sock.send(("USER " + username + "\r\n").encode())
                    data = self.sock.recv(1024).decode()
                    if "200" in data:
                        self.sock.send(("PASS " + password + "\r\n").encode())
                        data = self.sock.recv(1024).decode()
                        if "200" in data:
                            print("Inicio de sesión exitoso.")
                            self.username = username
                            gui.actualizar_ventana_principal(True)
                        else:
                            gui.inicio_sesion_container.remove()
                            gui.ventana_iniciar_sesion(False)
                    else:
                        gui.inicio_sesion_container.remove()
                        gui.ventana_iniciar_sesion(False)
                else:
                    gui.inicio_sesion_container.remove()
                    gui.ventana_iniciar_sesion(False)
            except Exception as e:
                print("Error al conectar al servidor:", e)
        else:
            print("No se pudo obtener la dirección IP.")


    def cerrar_sesion(self):
        self.sock.send("QUIT\r\n".encode())
        self.sock.close()


    def obtener_ip(self):
        # Crear un socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Conectar a un servidor remoto
            sock.connect(("www.google.com", 80))
            # Obtener la dirección IP, usamos este método ya que hay otros pero no funcionan si usas la VPN
            ip = sock.getsockname()[0]
            return ip
        except Exception as e:
            print("Error al obtener la dirección IP de la VPN:", e)
            return None
        finally:
            # Cerrar el socket
            sock.close()


    def is_json_string(self, txt):
        return txt.startswith("{")


    def obtener_leaderboard(self):
        self.sock.send("GET_LEADERBOARD\r\n".encode())
        data_unique = ""
        data = []
        fin = False
        while fin == False:
            data_unique = self.sock.recv(1024).decode()
            lineas = data_unique.split("\r\n")[:-1]
            for linea in lineas:
                print(linea)
                if self.is_json_string(linea):
                    data += [json.loads(linea)]
                elif linea.startswith("202"):
                    fin = True
        return data


    def enviar_salto(self, grupo, altura, fecha):
        datos = 'SEND_DATA {"nombre":"' + self.username + '", "grupo_ProMu":"' + grupo + '", "altura": ' + str(altura) + ',"fecha":"' + str(fecha) + '"}\r\n'
        print(datos)
        self.sock.send(datos.encode())
        print(self.sock.recv(1024).decode())
        print(fecha)


    def formato_fecha(self):
        fecha = str(datetime.datetime.now().date())
        fecha = fecha.split("-")
        if fecha[1] == "01":
            fecha[1] = "enero"
        elif fecha[1] == "02":
            fecha[1] = "febrero"
        elif fecha[1] == "03":
            fecha[1] = "marzo"
        elif fecha[1] == "04":
            fecha[1] = "abril"
        elif fecha[1] == "05":
            fecha[1] = "mayo"
        elif fecha[1] == "06":
            fecha[1] = "junio"
        elif fecha[1] == "07":
            fecha[1] = "julio"
        elif fecha[1] == "08":
            fecha[1] = "agosto"
        elif fecha[1] == "09":
            fecha[1] = "septiembre"
        elif fecha[1] == "10":
            fecha[1] = "octubre"
        elif fecha[1] == "11":
            fecha[1] = "noviembre"
        elif fecha[1] == "12":
            fecha[1] = "diciembre"
        fecha = str(fecha[2] + "-" + fecha[1] + "-" + fecha[0])
        return fecha


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("APP")
        self.root.geometry("750x600")
        self.arqred = ARQRED()
        self.logeado = False
        self.crear_ventana_principal()
        self.root.mainloop()

    def barra_menu(self):
        def file_function():
            tk.messagebox.showinfo("File", "File function")

        def edit_function():
            tk.messagebox.showinfo("Edit", "Edit function")

        def iniciar_sesion():
            self.ventana_iniciar_sesion()

        def cerrar_sesion():
            self.arqred.cerrar_sesion()
            self.crear_ventana_principal()


        def home():
            self.crear_ventana_principal()

        menubar = tk.Menu(self.root)
        if self.logeado:
            archivo_menu = tk.Menu(menubar, tearoff=0)
            archivo_menu.add_command(label="File option 1", command=file_function)
            archivo_menu.add_command(label="File option 2", command=file_function)
            menubar.add_cascade(label="Archivo", menu=archivo_menu)

            editar_menu = tk.Menu(menubar, tearoff=0)
            editar_menu.add_command(label="Edit option 1", command=edit_function)
            editar_menu.add_command(label="Edit option 2", command=edit_function)
            menubar.add_cascade(label="Editar", menu=editar_menu)

            menubar.add_command(label="Cerrar sesión", command=cerrar_sesion)
        else:
            menubar.add_command(label="Iniciar sesión", command=iniciar_sesion)
            menubar.add_command(label="Home", command=home)

        self.root.config(menu=menubar)

    def crear_ventana_principal(self):
        self.limpiar_ventana()
        self.barra_menu()

        self.bienvenida_frame = tk.Frame(self.root)
        self.bienvenida_frame.pack()

        imagen_bienvenida = tk.PhotoImage(file="imagen_bienvenida.png")  # Asegúrate de tener esta imagen
        label_imagen = tk.Label(self.bienvenida_frame, image=imagen_bienvenida)
        label_imagen.image = imagen_bienvenida
        label_imagen.pack()

        boton_invitado = tk.Button(self.bienvenida_frame, text="Acceder como invitado", command=self.acceder_como_invitado)
        boton_invitado.pack(pady=5)

        boton_iniciar_sesion = tk.Button(self.bienvenida_frame, text="Acceder como usuario registrado", command=self.ventana_iniciar_sesion)
        boton_iniciar_sesion.pack(pady=5)

    def limpiar_ventana(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def acceder_como_invitado(self):
        self.actualizar_ventana_principal(False)

    def ventana_iniciar_sesion(self, bool=True):
        self.limpiar_ventana()
        self.barra_menu()

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
            label_error = tk.Label(self.inicio_sesion_frame, text="Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo.", fg="red")
            label_error.pack(pady=5)

    def procesar_inicio_sesion(self):
        usuario = self.usuario_entry.get()
        password = self.password_entry.get()
        self.arqred.iniciar_sesion(usuario, password, self)

    def actualizar_ventana_principal(self, logeado):
        self.logeado = logeado
        self.limpiar_ventana()
        self.barra_menu()

        def open_file():
            # Abre el selector de fichero y obtiene la ruta del fichero seleccionado
            file_path = filedialog.askopenfilename(
                title="Seleccionar fichero",
                filetypes=(("Archivos de Excel", "*.xlsx"), ("Todos los archivos", "*.*"))
            )
        if logeado:
            self.enviar_frame = tk.Frame(self.root)
            self.enviar_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

            self.leaderboard_frame = tk.Frame(self.root)
            self.leaderboard_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)

            # Sección de enviar y analizar
            fichero_label = tk.Label(self.enviar_frame, text="Abrir fichero acelerometro")
            fichero_label.pack(pady=5)
            abrir_fichero = tk.Button(self.enviar_frame, text="Abrir fichero", command=open_file)
            abrir_fichero.pack(pady=5)

            analizar_label = tk.Label(self.enviar_frame, text="Analizar")
            analizar_label.pack(pady=5)
            analizar_button = tk.Button(self.enviar_frame, text="Analizar", command=lambda: print("Analizar"))
            analizar_button.pack(pady=5)

            enviar_label = tk.Label(self.enviar_frame, text="Enviar")
            enviar_label.pack(pady=5)
            enviar_button = tk.Button(self.enviar_frame, text="Enviar", command=lambda: print("Enviar"))
            enviar_button.pack(pady=5)

            # Sección de leaderboard
            leaderboard_data = self.arqred.obtener_leaderboard()
            leaderboard_text = tk.Label(self.leaderboard_frame, text="Leaderboard")
            leaderboard_text.pack(pady=5)

            leaderboard_info = "\n".join(
                [f"Usuario: {entry['nombre']}, Grupo: {entry['grupo_ProMu']}, Altura: {entry['altura']}, Fecha: {entry['fecha']}" for entry in leaderboard_data])
            leaderboard_label = tk.Label(self.leaderboard_frame, text=leaderboard_info)
            leaderboard_label.pack(pady=5)
        else:
            self.enviar_frame = tk.Frame(self.root)
            self.enviar_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)

            self.leaderboard_frame = tk.Frame(self.root)
            self.leaderboard_frame.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.BOTH, expand=True)

            # Sección de enviar y analizar
            fichero_label = tk.Label(self.enviar_frame, text="Abrir fichero acelerometro")
            fichero_label.pack(pady=5)
            abrir_fichero = tk.Button(self.enviar_frame, text="Abrir fichero", command=open_file)
            abrir_fichero.pack(pady=5)

            analizar_label = tk.Label(self.enviar_frame, text="Analizar")
            analizar_label.pack(pady=5)
            analizar_button = tk.Button(self.enviar_frame, text="Analizar", command=lambda: print("Analizar"))
            analizar_button.pack(pady=5)

            # Sección de leaderboard
            tk.Label(self.leaderboard_frame, text="Leaderboard Not Available.\nPorfavor, inicie sesión").pack(pady=5)



class Analisis:
    def __init__(self, filename="muestras-sep-coma.xlsx"):
        self.data = pd.read_excel(filename)
        self.tiempos = self.data["t"].values
        self.aceleracion_x = self.data["ax"].values
        self.aceleracion_y = self.data["ay"].values
        self.aceleracion_z = self.data["az"].values
        self.g = None  # Aceleración gravitatoria inicializada como None

    def calcular_aceleracion_gravitatoria(self):
        # Suponiendo que los primeros y últimos 10 puntos son los de reposo
        puntos_reposo = np.concatenate([self.aceleracion_z[:10], self.aceleracion_z[-10:]])
        self.g = np.mean(puntos_reposo)
        print(f"Aceleración gravitatoria calculada: {self.g} m/s^2")

    def ajustar_aceleracion(self):
        # Restar la aceleración gravitatoria de la componente Z
        self.aceleracion_z -= self.g

    def filtrar_datos(self):
        # Aplicar filtro gaussiano para suavizar los datos
        self.aceleracion_x = gf(self.aceleracion_x, sigma=2)
        self.aceleracion_y = gf(self.aceleracion_y, sigma=2)
        self.aceleracion_z = gf(self.aceleracion_z, sigma=2)

    def calcular_fuerza(self):
        # Calcular la fuerza resultante en cada eje
        masa = 70  # kg (suposición)
        self.fuerza_x = masa * self.aceleracion_x
        self.fuerza_y = masa * self.aceleracion_y
        self.fuerza_z = masa * self.aceleracion_z

    def calcular_velocidad(self):
        # Calcular la velocidad integrando la aceleración
        self.velocidad_x = cumulative_trapezoid(self.aceleracion_x, self.tiempos, initial=0)
        self.velocidad_y = cumulative_trapezoid(self.aceleracion_y, self.tiempos, initial=0)
        self.velocidad_z = cumulative_trapezoid(self.aceleracion_z, self.tiempos, initial=0)

    def calcular_desplazamiento(self):
        # Calcular el desplazamiento integrando la velocidad
        self.desplazamiento_x = cumulative_trapezoid(self.velocidad_x, self.tiempos, initial=0)
        self.desplazamiento_y = cumulative_trapezoid(self.velocidad_y, self.tiempos, initial=0)
        self.desplazamiento_z = cumulative_trapezoid(self.velocidad_z, self.tiempos, initial=0)

    def calcular_potencia(self):
        # Calcular la potencia como el producto punto de fuerza y velocidad
        self.potencia_x = self.fuerza_x * self.velocidad_x
        self.potencia_y = self.fuerza_y * self.velocidad_y
        self.potencia_z = self.fuerza_z * self.velocidad_z
        self.potencia_total = self.potencia_x + self.potencia_y + self.potencia_z

    def graficar_datos(self):
        # Crear las gráficas de los datos calculados
        fig, axs = plt.subplots(5, 1, figsize=(10, 20), sharex=True)

        axs[0].plot(self.tiempos, self.aceleracion_x, label='Aceleración X')
        axs[0].plot(self.tiempos, self.aceleracion_y, label='Aceleración Y')
        axs[0].plot(self.tiempos, self.aceleracion_z, label='Aceleración Z')
        axs[0].set_ylabel('Aceleración (m/s^2)')
        axs[0].legend()
        axs[0].grid()

        axs[1].plot(self.tiempos, self.fuerza_x, label='Fuerza X')
        axs[1].plot(self.tiempos, self.fuerza_y, label='Fuerza Y')
        axs[1].plot(self.tiempos, self.fuerza_z, label='Fuerza Z')
        axs[1].set_ylabel('Fuerza (N)')
        axs[1].legend()
        axs[1].grid()

        axs[2].plot(self.tiempos, self.velocidad_x, label='Velocidad X')
        axs[2].plot(self.tiempos, self.velocidad_y, label='Velocidad Y')
        axs[2].plot(self.tiempos, self.velocidad_z, label='Velocidad Z')
        axs[2].set_ylabel('Velocidad (m/s)')
        axs[2].legend()
        axs[2].grid()

        axs[3].plot(self.tiempos, self.desplazamiento_x, label='Desplazamiento X')
        axs[3].plot(self.tiempos, self.desplazamiento_y, label='Desplazamiento Y')
        axs[3].plot(self.tiempos, self.desplazamiento_z, label='Desplazamiento Z')
        axs[3].set_ylabel('Desplazamiento (m)')
        axs[3].legend()
        axs[3].grid()

        axs[4].plot(self.tiempos, self.potencia_x, label='Potencia X')
        axs[4].plot(self.tiempos, self.potencia_y, label='Potencia Y')
        axs[4].plot(self.tiempos, self.potencia_z, label='Potencia Z')
        axs[4].plot(self.tiempos, self.potencia_total, label='Potencia Total')
        axs[4].set_ylabel('Potencia (W)')
        axs[4].set_xlabel('Tiempo (s)')
        axs[4].legend()
        axs[4].grid()

        plt.show()

class Estadistica:
    def __init__(self):
        self.porcentiles()
    def porcentiles(self, sexo, altura_salto):
        if sexo == "M":
            if altura_salto <= 24.52:
                return (5, 0, 24.52, 24.52 - altura_salto)
            elif altura_salto <= 26.78 and altura_salto > 24.52:
                return (5, 24.52, 26.78, 26.78 - altura_salto)
            elif altura_salto <= 29.96 and altura_salto > 26.78:
                return (25, 26.78, 29.96, 29.96 - altura_salto)
            elif altura_salto <= 33.24 and altura_salto > 29.96:
                return (50, 29.96, 33.24, 33.24 - altura_salto)
            elif altura_salto <= 36.90 and altura_salto > 33.24:
                return (75, 33.24, 36.90, 36.90 - altura_salto)
            elif altura_salto <= 41.19 and altura_salto > 36.9:
                return (90, 41.19, 36.9, 41.19 - altura_salto)
            elif altura_salto <=43.49 and altura_salto > 41.19:
                return (95, 43.49, 41.19, 43.49 - altura_salto)
            elif altura_salto <= 70 and altura_salto > 43.49:
                return 100
            else:
                raise Exception("Errno6. Altura invalida, revise unidades. Unidad esperada cm")
        elif sexo == "F":
            if altura_salto <= 18:
                return (5, 0, 18, 18 - altura_salto)
            elif altura_salto <= 20.11 and altura_salto > 18:
                return (5, 18, 20.11, 20.11 - altura_salto)
            elif altura_salto <= 21.79 and altura_salto > 20.11:
                return (25, 20.11, 21.79, 21.79 - altura_salto)
            elif altura_salto <= 24.62 and altura_salto > 21.79:
                return (50, 21.79, 24.62, 24.62 - altura_salto)
            elif altura_salto <= 26.89 and altura_salto > 24.62:
                return (75, 24.62, 26.89, 26.89 - altura_salto)
            elif altura_salto <= 30.35 and altura_salto > 26.89:
                return (90, 30.35, 26.89, 30.35 - altura_salto)
            elif altura_salto <= 32.78 and altura_salto > 30.35:
                return (95, 32.78, 30.35, 32.78 - altura_salto)
            elif altura_salto <= 65 and altura_salto > 32.78:
                return 100
            else:
                raise Exception("Errno6. Altura invalida, revise unidades. Unidad esperada cm")
        else:
            raise ValueError("Errno7. Sexo debe ser M para masculino o F para femenino")


if __name__ == "__main__":
    analisis = Analisis()
    analisis.calcular_aceleracion_gravitatoria()  # Calcular la aceleración gravitatoria
    analisis.ajustar_aceleracion()  # Ajustar la aceleración Z
    analisis.filtrar_datos()
    analisis.calcular_fuerza()
    analisis.calcular_velocidad()
    analisis.calcular_desplazamiento()
    analisis.calcular_potencia()
    analisis.graficar_datos()
    ARQRED()
    gui = GUI()