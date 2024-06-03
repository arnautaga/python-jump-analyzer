import socket
import json
import datetime


class Redes:
    def __init__(self):
        self.dir_socket_servidor = ("158.42.188.200", 64010)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def iniciar_sesion(self, username, password, gui):
        self.username = username
        gui.menu(True)

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
                            self.username = username
                            gui.menu(True)
                        else:
                            gui.ventana_iniciar_sesion(False)
                    else:
                        gui.ventana_iniciar_sesion(False)
                else:
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

    def formatear_datos_leaderboard(self, data):
        c = 0
        for i in data:
            data[c] = list(i.values())
            c += 1
        data = [["Ranking", "Nombre", "Grupo ProMu", "Altura", "Fecha"]] + data[:10]
        return data

    def obtener_leaderboard(self):
        self.sock.send("GET_LEADERBOARD\r\n".encode())
        data_unique = ""
        data = []
        fin = False
        while fin == False:
            data_unique = self.sock.recv(1024).decode()
            lineas = data_unique.split("\r\n")[:-1]
            for linea in lineas:
                if self.is_json_string(linea):
                    data += [json.loads(linea)]
                elif linea.startswith("202"):
                    fin = True

        return self.formatear_datos_leaderboard(data)

    def enviar_salto(self, grupo, altura, fecha):
        datos = 'SEND_DATA {"nombre":"' + self.username + '", "grupo_ProMu":"' + grupo + '", "altura": ' + str(
            altura) + ',"fecha":"' + str(fecha) + '"}\r\n'
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

