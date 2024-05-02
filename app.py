import guizero as gz


class GUI:
    def __init__(self):
        self.root = gz.App(title="APP")
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

        boton_iniciar_sesion = gz.PushButton(ventana_bienvenida, text="Iniciar sesión", command=self.iniciar_sesion)
        boton_iniciar_sesion.tk.pack(pady=5)

    def acceder_como_invitado(self):
        # Lógica para acceder como invitado
        print("Accediendo como invitado")

    def iniciar_sesion(self):
        # Lógica para iniciar sesión
        print("Iniciando sesión")


if __name__ == "__main__":
    gui = GUI()
    gui.root.display()
