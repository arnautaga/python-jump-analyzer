import tkinter as tk

# Crear la ventana principal
root = tk.Tk()

# Configurar dimensiones de la ventana
root.geometry("500x300")

# Crear un lienzo (canvas) para colocar la imagen de fondo
canvas = tk.Canvas(root, width=500, height=300)
canvas.pack()

# Cargar la imagen PNG
imagen_fondo = tk.PhotoImage(file="../app/imagen_bienvenida.png")

# Colocar la imagen en el lienzo (canvas)
canvas.create_image(0, 0, anchor=tk.NW, image=imagen_fondo)

# Mostrar la ventana
root.mainloop()
