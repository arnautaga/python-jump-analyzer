import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid as cumtrapz

class Analisis:

    def __init__(self):
        gui = GUI()
    def leer_datos(self):
        df = pd.read_excel(gui.file_path) # TODO: PASS TO ARGUMENT
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