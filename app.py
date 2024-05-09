import guizero as gz
import socket
import json
import datetime

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
                            print("Error: ", data)
                    else:
                        print("Error: ", data)
                else:
                    print("Error: ", data)
            except Exception as e:
                print("Error al conectar al servidor:", e)
        else:
            print("No se pudo obtener la dirección IP.")

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
                if linea.startswith("202"):
                    fin = True
        return data

    def enviar_salto(self, grupo, altura):
        fecha = datetime.datetime.now().date()
        datos = 'SEND_DATA{"nombre":' + self.username + ', "grupo_ProMu":' + grupo + ', "altura":' + str(altura) + ',"fecha":' + str(fecha) + '}\r\n'

class GUI:
    def __init__(self):
        self.root = gz.App(title="APP")
        self.arqred = ARQRED()
        self.logeado = False  # Estado de inicio de sesión
        self.bienvenida_container = None
        self.inicio_sesion_container = None
        self.principal_container = None
        self.leaderboard_container = None
        self.crear_ventana_principal()

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

    def acceder_como_invitado(self):
        # Lógica para acceder como invitado
        print("Accediendo como invitado")
        self.actualizar_ventana_principal(False)  # Mostrar ventana principal como invitado

    def ventana_iniciar_sesion(self):
        # Limpiar contenedor de bienvenida y mostrar contenedor de inicio de sesión
        self.bienvenida_container.hide()
        self.inicio_sesion_container.show()

        # Añadir los labels y textboxes para introducir los datos
        label_login = gz.Text(self.inicio_sesion_container, text="Nombre de usuario:")
        label_login.tk.pack(pady=5)
        usuario = gz.TextBox(self.inicio_sesion_container)
        usuario.tk.pack(pady=5)
        label_password = gz.Text(self.inicio_sesion_container, text="Contraseña:")
        label_password.tk.pack(pady=5)
        password = gz.TextBox(self.inicio_sesion_container, hide_text=True)
        password.tk.pack(pady=5)

        # Boton para entrar en la app
        boton_iniciar_sesion = gz.PushButton(self.inicio_sesion_container, text="Iniciar sesión", command=lambda: self.arqred.iniciar_sesion(usuario.value, password.value, self))
        boton_iniciar_sesion.tk.pack(pady=5)

    def actualizar_ventana_principal(self, loged=False):
        self.logeado = loged  # Actualizar el estado de inicio de sesión
        self.principal_container.show()

        if loged:
            # Mostrar opciones para usuario logeado
            self.bienvenida_container.hide()
            self.inicio_sesion_container.hide()

            label = gz.Text(self.principal_container, text="¡Bienvenido!")
            boton_leaderboard = gz.PushButton(self.principal_container, text="Ver Leaderboard", command=self.ver_leaderboard)
            boton_leaderboard.tk.pack(pady=5)
        else:
            # Mostrar opciones para usuario invitado
            self.bienvenida_container.show()
            label = gz.Text(self.principal_container, text="¡Bienvenido, invitado!")
        label.tk.pack()

    def ver_leaderboard(self):
        if self.logeado:
            leaderboard = self.arqred.obtener_leaderboard()
            print(leaderboard)
            # Mostrar leaderboard en una nueva ventana
            ventana_leaderboard = gz.Window(self.root, title="Leaderboard")
            for entry in leaderboard:
                gz.Text(ventana_leaderboard, text=entry).tk.pack()
                print(type(entry))
        else:
            print("Debe iniciar sesión para ver la leaderboard.")


if __name__ == "__main__":
    gui = GUI()
    gui.root.display()
