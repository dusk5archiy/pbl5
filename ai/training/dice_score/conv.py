import tensorflow as tf

def conv2_tflite(inp_savedmodel_dir: str, out_tflite_filename: str):
    converter = tf.lite.TFLiteConverter.from_saved_model(inp_savedmodel_dir)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(out_tflite_filename, 'wb') as f:
        f.write(tflite_model)
    print(f"Score model converted to {out_tflite_filename}")