import tensorflow as tf
from keras import ops
from .bounding_box.iou import compute_ciou


class CIoULoss(tf.keras.losses.Loss):
    def __init__(self, bounding_box_format, eps=1e-7, **kwargs):
        super().__init__(**kwargs)
        self.eps = eps
        self.bounding_box_format = bounding_box_format

    def call(self, y_true, y_pred):
        y_pred = ops.convert_to_tensor(y_pred)
        y_true = ops.cast(y_true, y_pred.dtype)

        if y_pred.shape[-1] != 4:
            raise ValueError(
                "CIoULoss expects y_pred.shape[-1] to be 4 to represent the "
                f"bounding boxes. Received y_pred.shape[-1]={y_pred.shape[-1]}."
            )

        if y_true.shape[-1] != 4:
            raise ValueError(
                "CIoULoss expects y_true.shape[-1] to be 4 to represent the "
                f"bounding boxes. Received y_true.shape[-1]={y_true.shape[-1]}."
            )

        if y_true.shape[-2] != y_pred.shape[-2]:
            raise ValueError(
                "CIoULoss expects number of boxes in y_pred to be equal to the "
                "number of boxes in y_true. Received number of boxes in "
                f"y_true={y_true.shape[-2]} and number of boxes in "
                f"y_pred={y_pred.shape[-2]}."
            )

        ciou = compute_ciou(y_true, y_pred, self.bounding_box_format)
        return 1 - ciou

    def get_config(self):
        config = super().get_config()
        config.update(
            {
                "eps": self.eps,
            }
        )
        return config

