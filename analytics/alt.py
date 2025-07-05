import tensorflow as tf
from tensorflow import keras

# Neural network for multi-output regression
model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(X.shape[1],)),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(64, activation='relu'),
    keras.layers.Dropout(0.2),
    keras.layers.Dense(32, activation='relu'),
    keras.layers.Dense(len(target_columns), activation='linear')  # Output layer
])

model.compile(
    optimizer='adam',
    loss='mse',
    metrics=['mae']
)