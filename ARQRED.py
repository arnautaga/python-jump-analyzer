from socket import *


def conectar_servidor(username, password):
    # Dirección del servidor y puerto
    dir_socket_servidor = ("158.42.188.200", 64010)

    # Crear un objeto de socket TCP
    sock = socket(AF_INET, SOCK_STREAM)

    try:
        # Conectar al servidor
        data_dec = "a"
        contador = 0
        while "200" != data_dec and contador == 0:
            sock.connect(dir_socket_servidor)
            ip_equipo = gethostbyname(gethostname())
            sock.send(("HELLO " + str(ip_equipo)+"\r\n").encode())
            print(ip_equipo)
            data = sock.recv(1024)
            data_dec = data.decode()
        contador = 1
        while "200" != data_dec and contador == 1:
            sock.send(("USER" + str(username) + "\r\n").encode())
            data = sock.recv(1024)
            data_dec = data.decode()
        contador = 2
        while "200" != data_dec and contador == 2:
            sock.send(("PASS" + str(password) + "\r\n").encode())
            data = sock.recv(1024)
            data_dec = data.decode()
        print("conectado")

    except Exception as e:
        print("Error al conectar al servidor:", e)
    finally:
        sock.close()

if __name__ == "__main__":
    conectar_servidor("atabgar", 489)

