# INDICE:
# 
# aceleraciones:
# 
# a_v -> aceleracion vertical sacado de excel
# a_v_filtrado -> aceleracion vertical sacado de excel filtrado
# 
# a_vertical_real -> aceleracion vertical quitado la gravedad del movil
# a_v_filtrado_real -> aceleracion vertical quitado la gravedad del movil filtrado
# 
# a_v_real_recortada -> aceleracion vertical quitado la gravedad y datos de reposo
# a_v_real_filtrado_recortado -> aceleracion vertical quitado la gravedad del movil filtrado y datos de reposo
#
# a_v_recortado -> aceleracion vertical sacado de excel recortado (usado para fuerza)
# a_filtrado_recortado -> aceleracion vertical sacado de excel filtrado recortado (usado para fuerza)
# 
# fuerzas:
# 
# fuerza -> fuerza con datos sacado de excel recortado
# fuerza_filtrada -> fuerza con datos sacado de excel filtrado recortado
# fuerza_maxima -> fuerza maxima
# 
# velocidades:
# 
# velocidad -> velocidad con a_vertical_real
# velocidad_filtrada -> velocidad con a_v_filtrado_real
# velocidad_maxima -> velocidad maxima
# 
# desplazamiento:
# 
# desplazamiento -> desplazamiento sacado de velocidad
# desplazamiento_filtrada -> desplazamiento con velocidad_filtrado
# altura_salto -> altura del salto
#
# potencia:
# 
# potencia -> potencia sacado de la fuerza
# potencia_filtrada -> potencia filtrada sacado de la fuerza_filtrada
# potencia_maxima -> potencia maxima

import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid

# Leer el archivo Excel
fichero = "muestras-sep-coma.xlsx"
df = pd.read_excel(fichero)

# Obtener los datos de tiempo y aceleración vertical
tiempo = df.values[1:, 0].astype(float)
ay = df.values[1:, 3].astype(float)
a = df.values[1:, 1].astype(float)

# Calcular la aceleración vertical con signo
signo_ay = np.sign(ay)
a_v = a * signo_ay

# Aplicar filtro gaussiano a la aceleración vertical
a_v_filtrado = gf(a_v, sigma=2)  # Aumentar el sigma para un suavizado más agresivo

# Gráfica de las aceleraciones suavizadas
# plt.plot(tiempo, a_v, label="Datos originales de aceleración (sin restar la gravedad del móvil)")
# plt.plot(tiempo, a_v_filtrado, label="Filtro gaussiano")
# plt.xlabel('Tiempo')
# plt.ylabel('Aceleración en y')
# plt.grid(True)
# plt.legend()
# plt.show()

# --------ESTOS PASOS SON PARA SACAR LA GRAVEDAD DEL MOVIL:--------

# Encontrar los índices correspondientes al rango de tiempo de 0 a 0.6 segundos
indice_inicio=np.where(tiempo>=0)[0][0]
indice_fin=np.where(tiempo>=0.6)[0][0]

# Calcular la aceleración media durante este período
aceleracion_gravitatoria=np.mean(a_v[indice_inicio:indice_fin])
print("La gravedad estimada del movil es:",aceleracion_gravitatoria)

# --------ESTOS SON DATOS DE ACELERACION QUITADO LA GRAVEDAD DE MOVIL:--------

a_vertical_real=a_v-aceleracion_gravitatoria
a_v_filtrado_real=gf(a_vertical_real,sigma=2)

# plt.plot(tiempo,a_vertical_real,label="Aceleración con gravedad restada")
# plt.plot(tiempo,a_v_filtrado_real,label="Filtro gaussiano")
# plt.xlabel('Tiempo')
# plt.ylabel('Aceleración en y')
# plt.grid(True)
# plt.legend()
# plt.show()

# --------ESTOS SON CODIGOS PARA CORTAR DATOS EN REPOSO:--------

# Identificar el índice donde la aceleración empieza a desviarse significativamente de cero
desviacion=np.where(np.abs(a_vertical_real)>0.6)[0][0]
indice_inicio_salto=desviacion-75

# Recortar los datos para quedarnos solo con la información del salto
tiempo_recortado=tiempo[indice_inicio_salto:]
tiempo_recortado-=tiempo_recortado[0] # Ajustar el tiempo para que comience en 0

a_v_real_recortada=a_vertical_real[indice_inicio_salto:]
a_v_real_filtrado_recortado=a_v_filtrado_real[indice_inicio_salto:]

# Esto para la fuerza, que tiene que ser con aceleracion original cortado
a_v_recortado=a_v[indice_inicio_salto:]
a_filtrado_recortado=a_v_filtrado[indice_inicio_salto:]

# --------ESTOS SON CODIGOS PARA SACAR MAX MIN DE ACELERACION:--------

maximos = np.argmax(a_v_real_recortada)
minimos = np.argmin(a_v_real_filtrado_recortado)
diferencia = maximos - minimos

# Calculamos la diferencia absoluta entre puntos adyacentes
diferencia_absoluta = np.abs(np.diff(a_v_real_filtrado_recortado))
#saca la media con mean
media = np.mean(diferencia_absoluta)
#luego súmale un poquito para el umbral
umbral = media + 0.005*(max(diferencia_absoluta)-media)
#Obtenemos el punto s
indice_cambio_brusco = np.argmax(diferencia_absoluta > umbral)

aceleracion_maxima=max(a_v_real_filtrado_recortado[indice_cambio_brusco:minimos])
print('La aceleracion maxima durante el vuelo es: {0:.2f} m/s²'.format(aceleracion_maxima))

plt.plot(tiempo_recortado, a_v_real_recortada, label="Aceleración con gravedad restada")
plt.plot(tiempo_recortado, a_v_real_filtrado_recortado, label="Filtro gaussiano")

plt.plot(tiempo_recortado[maximos], a_v_real_filtrado_recortado[maximos], "x", label="L")
plt.plot(tiempo_recortado[minimos], a_v_real_filtrado_recortado[minimos], "x", label="TO")
plt.fill_between(tiempo_recortado[minimos:maximos], a_v_real_filtrado_recortado[minimos], a_v_real_filtrado_recortado[maximos], alpha=0.3, label='Intervalo TIA')
plt.plot(tiempo_recortado[indice_cambio_brusco], a_v_real_filtrado_recortado[indice_cambio_brusco], "x", label="s")

plt.xlabel('Tiempo')
plt.ylabel('Aceleración en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON PASOS PARA CALCULAR LA FUERZA:--------

#aceleracion usada tiene que ser sin quitar la g de movil?
masa=60
# masa=float(input('Indique su masa en kilo:'))
fuerza=a_v_recortado*masa
fuerza_filtrado=a_filtrado_recortado*masa

# --------ESTOS SON CODIGOS PARA SACAR MAX MIN DE FUERZA:--------

maximos = np.argmax(fuerza)
minimos = np.argmin(fuerza_filtrado)
diferencia = maximos - minimos

# Calculamos la diferencia absoluta entre puntos adyacentes
diferencia_absoluta = np.abs(np.diff(fuerza_filtrado))
#saca la media con mean
media = np.mean(diferencia_absoluta)
#luego súmale un poquito para el umbral
umbral = media + 0.005*(max(diferencia_absoluta)-media)
#Obtenemos el punto s
indice_cambio_brusco = np.argmax(diferencia_absoluta > umbral)

fuerza_maxima=max(fuerza_filtrado[indice_cambio_brusco:minimos])
print('La fuerza maxima durante el vuelo es: {0:.2f} N'.format(fuerza_maxima))

plt.plot(tiempo_recortado,fuerza,label="Fuerza")
plt.plot(tiempo_recortado,fuerza_filtrado,label="Fuerza filtrada")

plt.plot(tiempo_recortado[maximos], fuerza_filtrado[maximos], "x", label="L")
plt.plot(tiempo_recortado[minimos], fuerza_filtrado[minimos], "x", label="TO")
plt.fill_between(tiempo_recortado[minimos:maximos], fuerza_filtrado[minimos], fuerza_filtrado[maximos], color='orange', alpha=0.3, label='Intervalo TIA')
plt.plot(tiempo_recortado[indice_cambio_brusco], fuerza_filtrado[indice_cambio_brusco], "x", label="s")

plt.xlabel('Tiempo')
plt.ylabel('Fuerza en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CALCULAR LA VELOCIDAD--------

def primitivaNumerica(variable,tiempo,y0):
    return cumulative_trapezoid(variable,x=tiempo,initial=y0)

#se usa aceleracion quitada la gravedad, no estoy segura de si es cortada o no cortada

# Calcula la velocidad integrando numéricamente la aceleración

velocidad=primitivaNumerica(a_v_real_recortada,tiempo_recortado,0)
velocidad_filtrado=primitivaNumerica(a_v_real_filtrado_recortado,tiempo_recortado,0)

# --------ESTOS SON CODIGOS PARA SACAR MAX MIN DE VELOCIDAD:--------

maximos = np.argmax(velocidad)
minimos = np.argmin(velocidad_filtrado)
diferencia = maximos - minimos

# Calculamos la diferencia absoluta entre puntos adyacentes
diferencia_absoluta = np.abs(np.diff(velocidad_filtrado))
#saca la media con mean
media = np.mean(diferencia_absoluta)
#luego súmale un poquito para el umbral
umbral = media + 0.005*(max(diferencia_absoluta)-media)
#Obtenemos el punto s
indice_cambio_brusco = np.argmax(diferencia_absoluta > umbral)

velocidad_maxima=max(velocidad_filtrado)
print('La velocidad maxima durante su vuelo es: {0:.2f} m/s.'.format(velocidad_maxima))

plt.plot(tiempo_recortado,velocidad,label="Velocidad")
plt.plot(tiempo_recortado,velocidad_filtrado,label="Velocidad filtrada")

plt.plot(tiempo_recortado[maximos], velocidad_filtrado[maximos], "x", label="TO")
plt.plot(tiempo_recortado[minimos], velocidad_filtrado[minimos], "x", label="L")
plt.plot(tiempo_recortado[indice_cambio_brusco], velocidad_filtrado[indice_cambio_brusco], "x", label="s")

plt.xlabel('Tiempo')
plt.ylabel('Velocidad en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CALCULAR EL DESPLAZAMIENTO--------

desplazamiento=primitivaNumerica(velocidad,tiempo_recortado,0)
desplazamiento_filtrado=primitivaNumerica(velocidad_filtrado,tiempo_recortado,0)

altura_saltado=(velocidad_maxima**2)/(2*aceleracion_gravitatoria)
print('La altura saltado es: {0:.2f} metros.'.format(altura_saltado))

plt.plot(tiempo_recortado,desplazamiento,label="Desplazamiento")
plt.plot(tiempo_recortado,desplazamiento_filtrado,label="Desplazamiento filtrado")

plt.xlabel('Tiempo')
plt.ylabel('Desplazamiento en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CALCULAR LA POTENCIA--------

#Calcula la potencia multiplicando la velocidad por la fuerza recortada
potencia=velocidad*fuerza
potencia_filtrada=velocidad_filtrado*fuerza_filtrado

# --------ESTOS SON CODIGOS PARA SACAR MAX MIN DE POTENCIA:--------

maximos = np.argmax(potencia)
minimos = np.argmin(potencia_filtrada)
diferencia = maximos - minimos

# Calculamos la diferencia absoluta entre puntos adyacentes
diferencia_absoluta = np.abs(np.diff(potencia_filtrada))
#saca la media con mean
media = np.mean(diferencia_absoluta)
#luego súmale un poquito para el umbral
umbral = media + 0.005*(max(diferencia_absoluta)-media)
#Obtenemos el punto s
indice_cambio_brusco = np.argmax(diferencia_absoluta > umbral)

potencia_maxima_vuelo=max(potencia_filtrada[indice_cambio_brusco:minimos])
print('La potencia maxima durante el vuelo es: {0:.2f} W'.format(potencia_maxima_vuelo))

plt.plot(tiempo_recortado,potencia,label="Potencia")
plt.plot(tiempo_recortado,potencia_filtrada,label="Potencia filtrada")

plt.plot(tiempo_recortado[maximos], potencia_filtrada[maximos], "x", label="TO")
plt.plot(tiempo_recortado[minimos], potencia_filtrada[minimos], "x", label="L")
plt.plot(tiempo_recortado[indice_cambio_brusco], potencia_filtrada[indice_cambio_brusco], "x", label="s")

plt.xlabel('Tiempo')
plt.ylabel('Potencia en y')
plt.grid(True)
plt.legend()
plt.show()