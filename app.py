import guizero as gz
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
        self.root = gz.App(title="APP")
        self.arqred = ARQRED()
        self.logeado = False  # Estado de inicio de sesión
        self.bienvenida_container = None
        self.inicio_sesion_container = None
        self.principal_container = None
        self.leaderboard_container = None
        self.menu = None
        self.crear_ventana_principal()


    def barra_menu(self):
        def file_function():
            print("File function")

        def edit_function():
            print("Edit function")

        def iniciar_sesion():
            self.ventana_iniciar_sesion()

        def cerrar_sesion():
            self.arqred.cerrar_sesion()
            self.actualizar_ventana_principal(False)

        if self.logeado:
            self.menu = gz.MenuBar(self.root,
                                   toplevel=["Archivo", "Editar", "Ventana", "Herramientas", "Historial", "Ayuda",
                                             "Acerca de", "Salir"],
                                   options=[
                                       [["File option 1", file_function], ["File option 2", file_function]],
                                       [["Edit option 1", edit_function], ["Edit option 2", edit_function]],
                                       [["Edit option 1", edit_function]],
                                       [["File option 1", file_function], ["File option 2", file_function]],
                                       [["Edit option 1", edit_function], ["Edit option 2", edit_function]],
                                       [["Edit option 1", edit_function]],
                                       [["File option 1", file_function], ["File option 2", file_function]],
                                       [["Cerrar sesión", cerrar_sesion]]
                                   ])
        else:
            self.menu = gz.MenuBar(self.root,
                                   toplevel=["Acceder"],
                                   options=[
                                       [["Iniciar sesión", iniciar_sesion]],
                                   ])


    def actualizar_barra_menu(self):
        # Destruye la barra de menú actual y vuelve a crearla para reflejar el estado de inicio de sesión actual
        if self.menu:
            self.menu.tk.destroy()
        self.barra_menu()


    def crear_ventana_principal(self):
        # Contenedor principal
        self.principal_container = gz.Box(self.root)

        # Contenedor para la bienvenida
        self.bienvenida_container = gz.Box(self.principal_container)
        imagen_bienvenida = gz.Picture(self.bienvenida_container, image="imagen_bienvenida.png")
        imagen_bienvenida.tk.pack()
        boton_invitado = gz.PushButton(self.bienvenida_container, text="Acceder como invitado",
                                       command=self.acceder_como_invitado)
        boton_invitado.tk.pack(pady=5)
        boton_iniciar_sesion = gz.PushButton(self.bienvenida_container, text="Acceder como usuario registrado",
                                             command=self.ventana_iniciar_sesion)
        boton_iniciar_sesion.tk.pack(pady=5)

        # Contenedor para el inicio de sesión
        self.inicio_sesion_container = gz.Box(self.principal_container)

        # Contenedor para leaderboard
        self.leaderboard_container = gz.Box(self.principal_container)

        # Crear la barra de menú inicial
        self.barra_menu()


    def acceder_como_invitado(self):
        # Lógica para acceder como invitado
        print("Accediendo como invitado")
        self.actualizar_ventana_principal(False)  # Mostrar ventana principal como invitado


    def ventana_iniciar_sesion(self, bool=True):
        # Limpiar contenedor de bienvenida y mostrar contenedor de inicio de sesión
        self.bienvenida_container.hide()
        self.inicio_sesion_container.show()

        # Añadir los labels y textboxes para introducir los datos
        label_login = gz.Text(self.inicio_sesion_container, text="Nombre de usuario:")
        label_login.tk.pack(pady=5)
        usuario = gz.TextBox(self.inicio_sesion_container, hide_text=True)
        usuario.tk.pack(pady=5)
        label_password = gz.Text(self.inicio_sesion_container, text="Contraseña:")
        label_password.tk.pack(pady=5)
        password = gz.TextBox(self.inicio_sesion_container, hide_text=True)
        password.tk.pack(pady=5)

        # Boton para entrar en la app
        boton_iniciar = gz.PushButton(self.inicio_sesion_container, text="Iniciar sesión",
                                      command=lambda: self.arqred.iniciar_sesion(usuario.value, password.value, self))
        boton_iniciar.tk.pack(pady=5)
        if bool == False:
            texto_error = gz.Text(self.inicio_sesion_container,
                                  text="Usuario o contraseña incorrectos. Por favor, inténtelo de nuevo.")
            texto_error.tk.pack(pady=5)
        print("Inicio de sesión")


    def actualizar_ventana_principal(self, logeado):
        self.logeado = logeado  # Actualizar el estado de inicio de sesión
        self.actualizar_barra_menu()  # Actualizar la barra de menú

        # Limpiar el contenedor principal
        self.principal_container.clear()

        if logeado:
            # Mostrar opciones para usuarios registrados
            self.bienvenida_container.hide()
            self.leaderboard_container.show()
            leaderboard_data = self.arqred.obtener_leaderboard()
            leaderboard_text = gz.Text(self.leaderboard_container, text="Leaderboard")
            leaderboard_text.tk.pack(pady=5)
            leaderboard_info = "\n".join(
                [f"Usuario: {entry['nombre']}, Grupo: {entry['grupo_ProMu']}, Altura: {entry['altura']}, Fecha: {entry['fecha']}" for entry in leaderboard_data])
            leaderboard_label = gz.Text(self.leaderboard_container, text=leaderboard_info)
            leaderboard_label.tk.pack(pady=5)
        else:
            # Mostrar bienvenida para usuarios no registrados o invitados
            self.bienvenida_container.show()
            self.leaderboard_container.hide()


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
    gui.root.display()