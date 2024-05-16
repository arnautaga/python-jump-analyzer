import pandas
import numpy as np
from scipy.ndimage import gaussian_filter1d as gf
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz

# INDICE:
# 
# aceleraciones:
# 
# a_v -> aceleracion vertical sacado de excel
# a_filtrado -> aceleracion vertical sacado de excel filtrado
# a_vertical_real -> aceleracion vertical quitado la gravedad del movil
# a_v_filtrado -> aceleracion vertical quitado la gravedad del movil filtrado
# a_v_recortada -> aceleracion vertical quitado la gravedad y datos de reposo
# a_v_filtrado_recortado -> aceleracion vertical quitado la gravedad del movil filtrado y datos de reposo
#
# fuerzas:
# 
# fuerza -> fuerza con datos sacado de excel
# fuerza_filtrado -> fuerza con datos sacado de excel filtrado
# 
# velocidades:
# 
# velocidad -> velocidad con a_vertical_real
# velocidad_filtrado -> velocidad con a_v_filtrado
# 
# desplazamiento:
# 
# desplazamiento -> desplazamiento sacado de velocidad
# desplazamiento_filtrado -> desplazamiento con velocidad_filtrado
#
# potencia:
# 
# potencia -> potencia sacado de la fuerza_recortada
# potencia_filtrada -> potencia filtrada sacado de la fuerza_recortada_filtrada
# 

# Leer el archivo Excel
fichero = "muestras-sep-coma.xlsx"
df = pandas.read_excel(fichero)

# Obtener los datos de tiempo y aceleración vertical
tiempo = df.values[1:, 0].astype(float)
ay = df.values[1:, 3].astype(float)
a = df.values[1:, 1].astype(float) #no se si sirve

# Calcular la aceleración vertical con signo
signo_ay = np.sign(ay)
a_v = a * signo_ay

# Aplicar filtro gaussiano a la aceleración vertical
a_filtrado = gf(a_v, sigma=1)

# Gráfica de las aceleraciones suavizadas
plt.plot(tiempo, a_v, label="Datos originales de aceleración (sin restar la gravedad del móvil)")
plt.plot(tiempo, a_filtrado, label="Filtro gaussiano")
plt.xlabel('Tiempo')
plt.ylabel('Aceleración en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS PASOS SON PARA SACAR LA GRAVEDAD DEL MOVIL:--------

# Encontrar los índices correspondientes al rango de tiempo de 0 a 0.6 segundos
indice_inicio = np.where(tiempo >= 0)[0][0]
indice_fin = np.where(tiempo >= 0.6)[0][0]

# Calcular la aceleración media durante este período
aceleracion_gravitatoria = np.mean(a_v[indice_inicio:indice_fin])
print("La gravedad estimada del salto es:", aceleracion_gravitatoria)

# --------ESTOS SON DATOS DE ACELERACION QUITADO LA GRAVEDAD DE MOVIL:--------

a_vertical_real = a_v - aceleracion_gravitatoria
a_v_filtrado = gf(a_vertical_real, sigma=1)

plt.plot(tiempo, a_vertical_real, label="Aceleración con gravedad restada")
plt.plot(tiempo, a_v_filtrado, label="Filtro gaussiano")
plt.xlabel('Tiempo')
plt.ylabel('Aceleración en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CORTAR DATOS EN REPOSO:--------

# Identificar el índice donde la aceleración empieza a desviarse significativamente de cero
cosa = np.where(np.abs(a_vertical_real) > 0.6)[0][0]
indice_inicio_salto = cosa - 75

# Recortar los datos para quedarnos solo con la información del salto
tiempo_recortado = tiempo[indice_inicio_salto:]
tiempo_recortado -= tiempo_recortado[0]  # Ajustar el tiempo para que comience en 0
a_v_recortada = a_vertical_real[indice_inicio_salto:]
a_v_filtrado_recortado = a_v_filtrado[indice_inicio_salto:]

plt.plot(tiempo_recortado, a_v_recortada, label="Aceleración con gravedad restada y recortada")
plt.plot(tiempo_recortado, a_v_filtrado_recortado, label="Filtro gaussiano recortado")
plt.xlabel('Tiempo')
plt.ylabel('Aceleración en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON PASOS PARA CALCULAR LA FUERZA:--------

masa = 80
# masa=float(input('Indique su masa en kilo:'))
fuerza = a_v_recortada * masa
fuerza_filtrado = a_v_filtrado_recortado * masa

plt.plot(tiempo_recortado, fuerza, label="Fuerza")
plt.plot(tiempo_recortado, fuerza_filtrado, label="Fuerza filtrada")
plt.xlabel('Tiempo')
plt.ylabel('Fuerza en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CALCULAR LA VELOCIDAD--------

def primitivaNumerica(variable, tiempo, y0):
    return cumtrapz(variable, x=tiempo, initial=y0)

#se usa aceleracion quitada la gravedad, no estoy segura de si es cortada o no cortada

# Calcula la velocidad integrando numéricamente la aceleración

velocidad = primitivaNumerica(a_v_recortada, tiempo_recortado, 0)
velocidad_filtrado = primitivaNumerica(a_v_filtrado_recortado, tiempo_recortado, 0)

plt.plot(tiempo_recortado, velocidad, label="Velocidad")
plt.plot(tiempo_recortado, velocidad_filtrado, label="Velocidad filtrada")
plt.xlabel('Tiempo')
plt.ylabel('Velocidad en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CALCULAR EL DESPLAZAMIENTO--------

desplazamiento = primitivaNumerica(velocidad, tiempo_recortado, 0)
desplazamiento_filtrado = primitivaNumerica(velocidad_filtrado, tiempo_recortado, 0)

plt.plot(tiempo_recortado, desplazamiento, label="Desplazamiento")
plt.plot(tiempo_recortado, desplazamiento_filtrado, label="Desplazamiento filtrado")
plt.xlabel('Tiempo')
plt.ylabel('Desplazamiento en y')
plt.grid(True)
plt.legend()
plt.show()

# --------ESTOS SON CODIGOS PARA CALCULAR LA POTENCIA--------

fuerza_recortada = fuerza[:len(tiempo_recortado)]
fuerza_filtrado_recortada = fuerza_filtrado[:len(tiempo_recortado)]

#Calcula la potencia multiplicando la velocidad por la fuerza recortada
potencia = velocidad * fuerza_recortada
potencia_filtrada = velocidad_filtrado * fuerza_filtrado_recortada

plt.plot(tiempo_recortado, potencia, label="Potencia")
plt.plot(tiempo_recortado, potencia_filtrada, label="Potencia filtrada")
plt.xlabel('Tiempo')
plt.ylabel('Potencia en y')
plt.grid(True)
plt.legend()
plt.show()

# falta sacar: aceleracion maxima, velocidad maxima en el despegue,
# potencia maxima, fuerza maxima, altura de salto, duración del vuelo
# -> revisar si estan bien los codigos hechos
# 
# graficos hechos-> aceleracion, fuerza, velocidad, desplazamiento, potencia
# 
# formula fuerza-> m*g+m*a=m*(av+g)
# formula potencial-> v*f
# formula aceleracion vertical con altura inicial-> modulo(am)*signo(ay) -> hecho
# formula aceleracion vertical-> a-g
# formula velocidad-> derivada de a
