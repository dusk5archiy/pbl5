from ai_edge_litert.interpreter import Interpreter
import numpy as np


class DotTfliteInference:
    def __init__(self, model_path: str):
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def _inference(self, x):
        if len(x.shape) == 3:
            x = x[None, ...]

        self.interpreter.set_tensor(self.input_details[0]["index"], x)
        self.interpreter.invoke()
        pred = self.interpreter.get_tensor(self.output_details[0]["index"])

        return pred

    def __call__(self, x):
        pred = self._inference(x)
        class_idx = int(np.argmax(pred[0]))

        return class_idx