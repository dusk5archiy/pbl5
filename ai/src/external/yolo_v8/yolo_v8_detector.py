import warnings

from . import bounding_box
from . import layers
import tensorflow as tf
import keras
from keras import ops
from .ciou_loss import CIoULoss
from .yolo_v8_label_encoder import (
    YOLOV8LabelEncoder,
)
from .__internal__ import unpack_input
from .funcs import (
    get_anchors,
    apply_path_aggregation_fpn,
    apply_yolo_v8_head,
    decode_regression_to_boxes,
    dist2bbox
)
from .task import Task
from .utils_train import get_feature_extractor

class YOLOV8Detector(Task):
    def __init__(
        self,
        backbone,
        num_classes,
        bounding_box_format,
        fpn_depth=2,
        label_encoder=None,
        prediction_decoder=None,
        **kwargs,
    ):
        extractor_levels = ["P3", "P4", "P5"]
        extractor_layer_names = [
            backbone.pyramid_level_inputs[i] for i in extractor_levels
        ]
        feature_extractor = get_feature_extractor(
            backbone, extractor_layer_names, extractor_levels
        )

        images = tf.keras.layers.Input(feature_extractor.input_shape[1:])
        features = list(feature_extractor(images).values())

        fpn_features = apply_path_aggregation_fpn(
            features, depth=fpn_depth, name="pa_fpn"
        )

        outputs = apply_yolo_v8_head(
            fpn_features,
            num_classes,
        )

        # To make loss metrics pretty, we use a no-op layer with a good name.
        boxes = tf.keras.layers.Concatenate(axis=1, name="box")([outputs["boxes"]])
        scores = tf.keras.layers.Concatenate(axis=1, name="class")(
            [outputs["classes"]]
        )

        outputs = {"boxes": boxes, "classes": scores}
        super().__init__(inputs=images, outputs=outputs, **kwargs)

        self.bounding_box_format = bounding_box_format
        self.prediction_decoder = (
            prediction_decoder
            or layers.NonMaxSuppression(
                bounding_box_format=bounding_box_format,
                from_logits=False,
                confidence_threshold=0.2,
                iou_threshold=0.7,
            )
        )
        self.backbone = backbone
        self.fpn_depth = fpn_depth
        self.num_classes = num_classes
        self.label_encoder = label_encoder or YOLOV8LabelEncoder(
            num_classes=num_classes
        )

    def compile(
        self,
        box_loss,
        classification_loss,
        box_loss_weight=7.5,
        classification_loss_weight=0.5,
        metrics=None,
        **kwargs,
    ):
        if metrics is not None:
            raise ValueError("User metrics not yet supported for YOLOV8")

        if isinstance(box_loss, str):
            if box_loss == "ciou":
                box_loss = CIoULoss(bounding_box_format="xyxy", reduction="sum")
            elif box_loss == "iou":
                warnings.warn(
                    "YOLOV8 recommends using CIoU loss, but was configured to "
                    "use standard IoU. Consider using `box_loss='ciou'` "
                    "instead."
                )
            else:
                raise ValueError(
                    f"Invalid box loss for YOLOV8Detector: {box_loss}. Box "
                    "loss should be a keras.Loss or the string 'ciou'."
                )
        if isinstance(classification_loss, str):
            if classification_loss == "binary_crossentropy":
                classification_loss = tf.keras.losses.BinaryCrossentropy(
                    reduction="sum"
                )
            else:
                raise ValueError(
                    "Invalid classification loss for YOLOV8Detector: "
                    f"{classification_loss}. Classification loss should be a "
                    "keras.Loss or the string 'binary_crossentropy'."
                )

        self.box_loss = box_loss
        self.classification_loss = classification_loss
        self.box_loss_weight = box_loss_weight
        self.classification_loss_weight = classification_loss_weight

        losses = {
            "box": self.box_loss,
            "class": self.classification_loss,
        }

        super().compile(loss=losses, **kwargs)

    def train_step(self, *args):
        data = args[-1]
        args = args[:-1]
        x, y = unpack_input(data)
        return super().train_step(*args, (x, y))

    def test_step(self, *args):
        data = args[-1]
        args = args[:-1]
        x, y = unpack_input(data)
        return super().test_step(*args, (x, y))

    def compute_loss(self, x, y, y_pred, sample_weight=None, **kwargs):
        box_pred, cls_pred = y_pred["boxes"], y_pred["classes"]

        pred_boxes = decode_regression_to_boxes(box_pred)
        pred_scores = cls_pred

        anchor_points, stride_tensor = get_anchors(image_shape=x.shape[1:])
        stride_tensor = ops.expand_dims(stride_tensor, axis=-1)

        gt_labels = y["classes"]

        mask_gt = ops.all(y["boxes"] > -1.0, axis=-1, keepdims=True)
        gt_bboxes = bounding_box.convert_format(
            y["boxes"],
            source=self.bounding_box_format,
            target="xyxy",
            images=x,
        )

        pred_bboxes = dist2bbox(pred_boxes, anchor_points)

        target_bboxes, target_scores, fg_mask = self.label_encoder(
            pred_scores,
            ops.cast(pred_bboxes * stride_tensor, gt_bboxes.dtype),
            anchor_points * stride_tensor,
            gt_labels,
            gt_bboxes,
            mask_gt,
        )

        target_bboxes /= stride_tensor
        target_scores_sum = ops.maximum(ops.sum(target_scores), 1)
        box_weight = ops.expand_dims(
            ops.sum(target_scores, axis=-1) * fg_mask,
            axis=-1,
        )

        y_true = {
            "box": target_bboxes * fg_mask[..., None],
            "class": target_scores,
        }
        y_pred = {
            "box": pred_bboxes * fg_mask[..., None],
            "class": pred_scores,
        }
        sample_weights = {
            "box": self.box_loss_weight * box_weight / target_scores_sum,
            "class": self.classification_loss_weight / target_scores_sum,
        }

        return super().compute_loss(
            x=x, y=y_true, y_pred=y_pred, sample_weight=sample_weights, **kwargs
        )

    def decode_predictions(
        self,
        pred,
        images,
    ):
        boxes = pred["boxes"]
        scores = pred["classes"]

        boxes = decode_regression_to_boxes(boxes)

        anchor_points, stride_tensor = get_anchors(image_shape=images.shape[1:])
        stride_tensor = ops.expand_dims(stride_tensor, axis=-1)

        box_preds = dist2bbox(boxes, anchor_points) * stride_tensor
        box_preds = bounding_box.convert_format(
            box_preds,
            source="xyxy",
            target=self.bounding_box_format,
            images=images,
        )

        return self.prediction_decoder(box_preds, scores)

    def predict_step(self, *args):
        outputs = super().predict_step(*args)
        if isinstance(outputs, tuple):
            return self.decode_predictions(outputs[0], args[-1]), outputs[1]
        else:
            return self.decode_predictions(outputs, args[-1])

    def get_config(self):
        return {
            "num_classes": self.num_classes,
            "bounding_box_format": self.bounding_box_format,
            "fpn_depth": self.fpn_depth,
            "backbone": tf.keras.saving.serialize_keras_object(self.backbone),
            "label_encoder": tf.keras.saving.serialize_keras_object(
                self.label_encoder
            ),
            "prediction_decoder": tf.keras.saving.serialize_keras_object(
                self.prediction_decoder
            ),
        }

    @classmethod
    def from_config(cls, config):
        config["backbone"] = tf.keras.saving.deserialize_keras_object(
            config["backbone"]
        )
        label_encoder = config.get("label_encoder")
        if label_encoder is not None and isinstance(label_encoder, dict):
            config["label_encoder"] = tf.keras.saving.deserialize_keras_object(
                label_encoder
            )
        prediction_decoder = config.get("prediction_decoder")
        if prediction_decoder is not None and isinstance(
            prediction_decoder, dict
        ):
            config["prediction_decoder"] = (
                keras.saving.deserialize_keras_object(prediction_decoder)
            )
        return cls(**config)