from .. import backend
from keras import ops
from .to_ragged import to_ragged
from .validate_format import validate_format


def mask_invalid_detections(bounding_boxes, output_ragged=False):
    # ensure we are complying with KerasCV bounding box format.
    info = validate_format(bounding_boxes)
    if info["ragged"]:
        raise ValueError(
            "`bounding_box.mask_invalid_detections()` requires inputs to be "
            "Dense tensors. Please call "
            "`bounding_box.to_dense(bounding_boxes)` before passing your boxes "
            "to `bounding_box.mask_invalid_detections()`."
        )
    if "num_detections" not in bounding_boxes:
        raise ValueError(
            "`bounding_boxes` must have key 'num_detections' "
            "to be used with `bounding_box.mask_invalid_detections()`."
        )

    boxes = bounding_boxes.get("boxes")
    classes = bounding_boxes.get("classes")
    confidence = bounding_boxes.get("confidence", None)
    num_detections = bounding_boxes.get("num_detections")

    # Create a mask to select only the first N boxes from each batch
    mask = ops.cast(
        ops.expand_dims(ops.arange(boxes.shape[1]), axis=0),
        num_detections.dtype,
    )
    mask = mask < num_detections[:, None]

    classes = ops.where(mask, classes, -ops.ones_like(classes))

    if confidence is not None:
        confidence = ops.where(mask, confidence, -ops.ones_like(confidence))

    # reuse mask for boxes
    mask = ops.expand_dims(mask, axis=-1)
    mask = ops.repeat(mask, repeats=boxes.shape[-1], axis=-1)
    boxes = ops.where(mask, boxes, -ops.ones_like(boxes))

    result = bounding_boxes.copy()

    result["boxes"] = boxes
    result["classes"] = classes
    if confidence is not None:
        result["confidence"] = confidence

    if output_ragged and backend.supports_ragged():
        return to_ragged(result)

    return result
