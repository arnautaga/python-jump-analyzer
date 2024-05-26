import tkinter as tk
from tkinter import filedialog
import socket
import json
import datetime
import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid as cumtrapz


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

    def __init__(self):
        pass
    def leer_datos(self, fichero):
        df = pd.read_excel(fichero)
        tiempo = df.values[1:, 0].astype(float)
        ay = df.values[1:, 3].astype(float)
        a = df.values[1:, 1].astype(float)
        return tiempo, ay, a

    # Función para aplicar un filtro Gaussiano a los datos
    def aplicar_filtro_gaussiano(self, dato, sigma=5):
        return gf(dato, sigma=sigma)

    # Función para calcular la aceleración vertical con signo
    def calcular_aceleracion_vertical(self, ay, a):
        signo_ay = np.sign(ay)
        a_v = a * signo_ay
        a_v_filtrado = self.aplicar_filtro_gaussiano(a_v)
        return a_v, a_v_filtrado

    # Función para estimar la gravedad del móvil
    def estimar_gravedad(self, tiempo, a_v):
        indice_inicio = np.where(tiempo >= 0)[0][0]
        indice_fin = np.where(tiempo >= 0.6)[0][0]
        aceleracion_gravitatoria = np.mean(a_v[indice_inicio:indice_fin])
        return aceleracion_gravitatoria

    # Función para restar la gravedad del móvil
    def restar_gravedad(self, a_v, aceleracion_gravitatoria):
        a_vertical_real = a_v - aceleracion_gravitatoria
        return a_vertical_real

    # Función para recortar los datos adicionales
    # !!a_v_recortado, a_filtrado_recortado para la fuerza, que tiene que ser con aceleracion original cortado
    def recortar_datos(self, tiempo, a_vertical_real, a_v, a_v_filtrado):
        desviacion = np.where(np.abs(a_vertical_real) > 0.6)[0][0]
        indice_inicio_salto = desviacion - 75

        tiempo_recortado = tiempo[indice_inicio_salto:] - tiempo[indice_inicio_salto]

        a_v_real_recortada = a_vertical_real[indice_inicio_salto:]
        a_v_filtrado_real = self.aplicar_filtro_gaussiano(a_vertical_real, sigma=2)
        a_v_real_filtrado_recortado = a_v_filtrado_real[indice_inicio_salto:]

        a_v_recortado = a_v[indice_inicio_salto:]
        a_filtrado_recortado = a_v_filtrado[indice_inicio_salto:]
        return tiempo_recortado, a_v_real_recortada, a_v_real_filtrado_recortado, a_v_recortado, a_filtrado_recortado

    # Función para calcular la primitiva numérica (integral acumulativa)
    def primitiva_numerica(self, variable, tiempo, y0=0):
        return cumtrapz(variable, x=tiempo, initial=y0)

    # Función para calcular la fuerza
    def calcular_fuerza(self, a_v_recortado, masa):
        fuerza = a_v_recortado * masa
        fuerza_filtrada = self.aplicar_filtro_gaussiano(fuerza, sigma=2)
        return fuerza, fuerza_filtrada

    # Función para calcular los valores máximo y mínimo de una señal
    def calcular_max_min(self, signal):
        maximo = np.argmax(signal)
        minimo = np.argmin(signal)
        return maximo, minimo

    # Función para identificar cambios abruptos en una señal

    def identificar_cambio_brusco(self, signal, sampling_rate=250, umbral=0.25):
        # Convertir 0.2 segundos a índice de muestra
        start_index = int(0.2 * sampling_rate)

        # Calcular la derivada de la señal
        derivada = np.gradient(signal)

        # Buscar el primer índice donde el cambio es mayor que el umbral, empezando desde start_index
        for i in range(start_index, len(derivada)):
            if np.abs(derivada[i]) > umbral:
                return i

        # Si no se encuentra ningún cambio brusco, retornar -1 o algún indicador apropiado
        return -1

    # Función para calcular velocidad, desplazamiento y potencia
    def calcular_cinematica(self, tiempo_recortado, a_v_real_recortada, a_v_real_filtrado_recortado, masa, fuerza,
                            fuerza_filtrada):
        velocidad = self.primitiva_numerica(a_v_real_recortada, tiempo_recortado)
        velocidad_filtrado = self.primitiva_numerica(a_v_real_filtrado_recortado, tiempo_recortado)

        desplazamiento = self.primitiva_numerica(velocidad, tiempo_recortado)
        desplazamiento_filtrado = self.primitiva_numerica(velocidad_filtrado, tiempo_recortado)

        potencia = velocidad * fuerza
        potencia_filtrada = velocidad_filtrado * fuerza_filtrada
        return velocidad, velocidad_filtrado, desplazamiento, desplazamiento_filtrado, potencia, potencia_filtrada

    # Función para calcular la altura del salto
    def calcular_altura_salto(self, velocidad_maxima, aceleracion_gravitatoria):
        altura_saltado = (velocidad_maxima ** 2) / (2 * aceleracion_gravitatoria)
        return altura_saltado

    # Función para graficar los resultados

    # !!!IMPORTANTE!!!: LA GRAFICA DE DESPLAZAMIENTO NO ES CORRECTO PORQUE
    # VA ACUMULANDO ERRORES DE INTEGRAR 2 VECES.
    # -> NO USARLO PARA LA APLICACION/ EXPLICARLO EN LA EXPOSICION

    # Usamos el maximo y minimo de velocidad para encontrar intervalo TIA de aceleracion, fuerza, velocidad etc

    def hacer_graficos(self, tiempo_recortado, a_v_real_recortada, a_v_real_filtrado_recortado, fuerza, fuerza_filtrada,
                       velocidad, velocidad_filtrado, desplazamiento, desplazamiento_filtrado, potencia,
                       potencia_filtrada,
                       maximos_velocidad, minimos_velocidad, indice_cambio_brusco_aceleracion,
                       indice_cambio_brusco_fuerza,
                       indice_cambio_brusco_velocidad, indice_cambio_brusco_desplazamiento,
                       indice_cambio_brusco_potencia):

        # aceleracion recortado y quitado la g

        plt.plot(tiempo_recortado, a_v_real_recortada, label="Aceleración con gravedad restada")
        plt.plot(tiempo_recortado, a_v_real_filtrado_recortado, label="Filtro gaussiano")

        plt.plot(tiempo_recortado[maximos_velocidad], a_v_real_filtrado_recortado[maximos_velocidad], "x",
                 label="Despegue")
        plt.plot(tiempo_recortado[minimos_velocidad], a_v_real_filtrado_recortado[minimos_velocidad], "x",
                 label="Landing")
        plt.fill_between(tiempo_recortado[maximos_velocidad:minimos_velocidad],
                         a_v_real_filtrado_recortado[minimos_velocidad], a_v_real_filtrado_recortado[maximos_velocidad],
                         alpha=0.3, color='red', label='Intervalo TIA')
        plt.plot(tiempo_recortado[indice_cambio_brusco_fuerza],
                 a_v_real_filtrado_recortado[indice_cambio_brusco_fuerza], "x", label="Inicio de impulso")
        # aqui he hecho un poco de trampa porque no sale bien si pongo indice_cambio_brusco_aceleracion, pero me sale bien con fuerza, explicamos en memoria que hemos hecho con indice_cambio_brusco_aceleracion

        plt.xlabel('Tiempo')
        plt.ylabel('Aceleración en y')
        plt.grid(True)
        plt.legend()
        plt.show()

        # fuerza recortado no quitado la g

        plt.figure()
        plt.plot(tiempo_recortado, fuerza, label="Fuerza")
        plt.plot(tiempo_recortado, fuerza_filtrada, label="Fuerza filtrada")

        plt.plot(tiempo_recortado[maximos_velocidad], fuerza_filtrada[maximos_velocidad], "x", label="Despegue")
        plt.plot(tiempo_recortado[minimos_velocidad], fuerza_filtrada[minimos_velocidad], "x", label="Landing")
        plt.fill_between(tiempo_recortado[maximos_velocidad:minimos_velocidad], fuerza_filtrada[minimos_velocidad],
                         fuerza_filtrada[maximos_velocidad], alpha=0.3, color='red', label='Intervalo TIA')
        plt.plot(tiempo_recortado[indice_cambio_brusco_fuerza], fuerza_filtrada[indice_cambio_brusco_fuerza], "x",
                 label="Inicio de impulso")

        plt.xlabel('Tiempo')
        plt.ylabel('Fuerza en y')
        plt.grid(True)
        plt.legend()
        plt.show()

        # velocidad recortado y g quitado

        plt.figure()
        plt.plot(tiempo_recortado, velocidad, label="Velocidad")
        plt.plot(tiempo_recortado, velocidad_filtrado, label="Velocidad filtrada")

        plt.plot(tiempo_recortado[maximos_velocidad], velocidad_filtrado[maximos_velocidad], "x", label="Despegue")
        plt.plot(tiempo_recortado[minimos_velocidad], velocidad_filtrado[minimos_velocidad], "x", label="Landing")
        plt.fill_between(tiempo_recortado[maximos_velocidad:minimos_velocidad], velocidad_filtrado[minimos_velocidad],
                         velocidad_filtrado[maximos_velocidad], alpha=0.3, color='red', label='Intervalo TIA')

        plt.xlabel('Tiempo')
        plt.ylabel('Velocidad en y')
        plt.grid(True)
        plt.legend()
        plt.show()

        # desplazamiento recortado y g quitado (No usar en aplicacion o explicar en exposicion)

        plt.figure()
        plt.plot(tiempo_recortado, desplazamiento, label="Desplazamiento")
        plt.plot(tiempo_recortado, desplazamiento_filtrado, label="Desplazamiento filtrado")

        plt.plot(tiempo_recortado[maximos_velocidad], desplazamiento_filtrado[maximos_velocidad], "x", label="Despegue")
        plt.plot(tiempo_recortado[minimos_velocidad], desplazamiento_filtrado[minimos_velocidad], "x", label="Landing")
        plt.fill_between(tiempo_recortado[maximos_velocidad:minimos_velocidad],
                         desplazamiento_filtrado[minimos_velocidad], desplazamiento_filtrado[maximos_velocidad],
                         alpha=0.3, color='red', label='Intervalo TIA')

        plt.xlabel('Tiempo')
        plt.ylabel('Desplazamiento en y')
        plt.grid(True)
        plt.legend()
        plt.show()

        # potencia recortado y g quitado

        plt.figure()
        plt.plot(tiempo_recortado, potencia, label="Potencia")
        plt.plot(tiempo_recortado, potencia_filtrada, label="Potencia filtrada")

        plt.plot(tiempo_recortado[maximos_velocidad], potencia_filtrada[maximos_velocidad], "x", label="Despegue")
        plt.plot(tiempo_recortado[minimos_velocidad], potencia_filtrada[minimos_velocidad], "x", label="Landing")
        plt.fill_between(tiempo_recortado[maximos_velocidad:minimos_velocidad], potencia_filtrada[minimos_velocidad],
                         potencia_filtrada[maximos_velocidad], alpha=0.3, color='red', label='Intervalo TIA')
        plt.plot(tiempo_recortado[indice_cambio_brusco_potencia], potencia_filtrada[indice_cambio_brusco_potencia], "x",
                 label="Inicio de impulso")

        plt.xlabel('Tiempo')
        plt.ylabel('Potencia en y')
        plt.grid(True)
        plt.legend()
        plt.show()

class Estadistica:
    def __init__(self):
        self.aux = None
    def porcentiles_altura(self, sexo, altura_salto):
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
    '''
    analisis = Analisis()
    analisis.calcular_aceleracion_gravitatoria()  # Calcular la aceleración gravitatoria
    analisis.ajustar_aceleracion()  # Ajustar la aceleración Z
    analisis.filtrar_datos()
    analisis.calcular_fuerza()
    analisis.calcular_velocidad()
    analisis.calcular_desplazamiento()
    analisis.calcular_potencia()
    analisis.graficar_datos()
    '''
    ARQRED()
    estadistica = Estadistica()
    estadistica.porcentiles_altura("M", 28)
    gui = GUI()