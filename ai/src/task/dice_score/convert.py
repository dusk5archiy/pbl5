import tensorflow as tf

def convert2_tflite(path: str, out_tflite_filename: str):
    model = tf.keras.models.load_model(path)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(out_tflite_filename, 'wb') as f:
        f.write(tflite_model)
    print(f"Score model converted to {out_tflite_filename}")