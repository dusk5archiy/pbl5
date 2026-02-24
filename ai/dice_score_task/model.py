import tensorflow as tf


def get_dice_score_model(
    classes: int = 6,
    image_resolution: tuple[int, int] = (32, 32),
    channels: int = 3,
):
    layers = tf.keras.layers
    model = tf.keras.Sequential([
        layers.Conv2D(32, 3, padding='same', activation='relu', input_shape=(*image_resolution, channels)),
        layers.MaxPooling2D(2, 2),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(2, 2),
        layers.Conv2D(128, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(2, 2),
        layers.Conv2D(256, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(2, 2),
        layers.Conv2D(512, 3, padding='same', activation='relu'),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(classes, activation='softmax')
    ])

    return model
