from .composables import process_predictions

from src.model.shared.args import DiceDetectionTaskArgs

from ai_edge_litert.interpreter import Interpreter
import tensorflow as tf

class DotTfliteInference:
    def __init__(self, model_path: str, args: DiceDetectionTaskArgs):
        self.args = args
        self.interpreter = Interpreter(model_path=model_path, num_threads=1)
        input_details = self.interpreter.get_input_details()
        self.interpreter.resize_tensor_input(
            input_details[0]["index"],
            [1, args.image_resolution[1], args.image_resolution[0], args.num_channels],
        )
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.interpreter.allocate_tensors()

    def _inference(self, x):
        if len(x.shape) == 3:
            x = tf.expand_dims(x, axis=0)

        self.interpreter.set_tensor(self.input_details[0]["index"], x)
        self.interpreter.invoke()

        boxes, classes = (
            self.interpreter.get_tensor(output["index"])
            for output in self.output_details
        )

        preds = {"boxes": boxes, "classes": classes}

        return process_predictions(
            preds,
            self.args.image_resolution,
            self.args.conf_threshold,
            self.args.iou_threshold,
        )

    def __call__(self, x):
        return self._inference(x).numpy()


