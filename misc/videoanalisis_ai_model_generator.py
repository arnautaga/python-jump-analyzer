import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from jumpAnalysis import VerticalJumpAnalyzer

# Definición del modelo
def build_model(input_shape):
    base_model = tf.keras.applications.MobileNetV2(input_shape=input_shape, include_top=False, weights='imagenet')
    base_model.trainable = False

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(256, activation='relu'),
        layers.Dense(2)  # 2 unidades para las coordenadas x e y del objeto
    ])

    return model

# Carga de los datos de jumpAnalysis
jump_analyzer = VerticalJumpAnalyzer()
data = jump_analyzer.get_jump_data()

# Preprocesamiento de los datos
# Aquí necesitamos preprocesar los datos para que sean compatibles con el formato de entrada del modelo
# Esto puede implicar redimensionar las imágenes, normalizar los píxeles, etc.

# Separación de los datos en entrenamiento y validación
train_data, val_data = data[:int(len(data)*0.8)], data[int(len(data)*0.8):]

# Extracción de características y etiquetas
x_train, y_train = np.array([sample['image'] for sample in train_data]), np.array([sample['coordinates'] for sample in train_data])
x_val, y_val = np.array([sample['image'] for sample in val_data]), np.array([sample['coordinates'] for sample in val_data])

# Compilación del modelo
model = build_model(input_shape=(224, 224, 3))  # Tamaño de entrada de las imágenes
model.compile(optimizer='adam', loss='mse')

# Entrenamiento del modelo
model.fit(x_train, y_train, validation_data=(x_val, y_val), epochs=10, batch_size=32)

# Evaluación del modelo
loss = model.evaluate(x_val, y_val)
print("Pérdida en el conjunto de validación:", loss)

# Guardado del modelo
model.save('object_tracking_model.h5')
