import tensorflow as tf

def convert2_tflite(
        path: str,
        out_tflite_filename: str,
        image_resolution: tuple[int, int],
        colored: bool=True
    ):
    num_channels = 3 if colored else 1
    print("[--INFO--] Importing model...")
    model = tf.keras.models.load_model(path)
    print("[--INFO--] Converting...")

    @tf.function(input_signature=[
        tf.TensorSpec(shape=[1, image_resolution[1], image_resolution[0], num_channels], dtype=tf.float32)
    ])
    def run_model(x):
        return model(x, training=False)
    
    concrete_func = run_model.get_concrete_function()
    converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
        
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]

    tflite_model = converter.convert()
    with open(out_tflite_filename, 'wb') as f:
        f.write(tflite_model)
    print(f"[--DONE--] Score model converted to {out_tflite_filename}")