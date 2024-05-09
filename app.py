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
                            gui.ventana_principal(True)
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
        self.abrir_ventana_bienvenida()

    def abrir_ventana_bienvenida(self):
        ventana_bienvenida = gz.Window(self.root, title="Bienvenida")

        # Agregar imagen
        imagen_bienvenida = gz.Picture(ventana_bienvenida, image="imagen_bienvenida.png")
        imagen_bienvenida.tk.pack()

        # Agregar botones
        boton_invitado = gz.PushButton(ventana_bienvenida, text="Acceder como invitado",
                                       command=self.acceder_como_invitado)
        boton_invitado.tk.pack(pady=5)

        boton_iniciar_sesion = gz.PushButton(ventana_bienvenida, text="Acceder como usuario registrado", command=self.ventana_iniciar_sesion)
        boton_iniciar_sesion.tk.pack(pady=5)

    def acceder_como_invitado(self):
        # Lógica para acceder como invitado
        print("Accediendo como invitado")
        self.ventana_principal(False)  # Mostrar ventana principal como invitado

    def ventana_iniciar_sesion(self):
        # Crear ventana para iniciar sesión
        ventana_login = gz.Window(self.root, title="Iniciar sesión")

        # Añadir los labels y textboxes para introducir los datos
        label_login = gz.Text(ventana_login, text="Nombre de usuario:")
        label_login.tk.pack(pady=5)
        usuario = gz.TextBox(ventana_login)
        usuario.tk.pack(pady=5)

        label_password = gz.Text(ventana_login, text="Contraseña:")
        label_password.tk.pack(pady=5)
        password = gz.TextBox(ventana_login, hide_text=True)
        password.tk.pack(pady=5)

        # Boton para entrar en la app
        boton_iniciar_sesion = gz.PushButton(ventana_login, text="Iniciar sesión", command=lambda: self.arqred.iniciar_sesion(usuario.value, password.value, self))
        boton_iniciar_sesion.tk.pack(pady=5)

    def ventana_principal(self, loged=False):
        self.logeado = loged  # Actualizar el estado de inicio de sesión
        ventana_principal = gz.Window(self.root, title="APP")
        if loged:
            # Mostrar opciones para usuario logeado
            label = gz.Text(ventana_principal, text="¡Bienvenido!")
            boton_leaderboard = gz.PushButton(ventana_principal, text="Ver Leaderboard", command=self.ver_leaderboard)
            boton_leaderboard.tk.pack(pady=5)
        else:
            # Mostrar opciones para usuario invitado
            label = gz.Text(ventana_principal, text="¡Bienvenido, invitado!")
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
