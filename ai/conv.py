import argparse
import tensorflow as tf

def convert_score_model():
    model_path = "../output/best_score_model"
    tflite_path = "../output/best_score_model.tflite"
    
    # Convert using tf.lite.TFLiteConverter
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"Score model converted to {tflite_path}")

def convert_detection_model():
    model_path = "../output/best_detection_model"
    tflite_path = "../output/best_detection_model.tflite"
    
    # Convert using tf.lite.TFLiteConverter
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"Detection model converted to {tflite_path}")

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--conv-score", action='store_true')
    parser.add_argument("--conv-detection", action='store_true')

    args = parser.parse_args()

    if args.conv_score:
        convert_score_model()
    elif args.conv_detection:
        convert_detection_model()

if __name__ == "__main__":
    main()
