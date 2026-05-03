from src.external.yolo_v8.bounding_box.iou import compute_ciou

import numpy as np
import tensorflow as tf

def get_gt_boxes(target_boxes: tf.Tensor, target_classes: tf.Tensor):
    gt_boxes = (
        tf.reshape(target_boxes, (-1, 4))
        if tf.rank(target_boxes) == 1
        else target_boxes
    )
    gt_classes = (
        tf.reshape(target_classes, (-1,))
        if tf.rank(target_classes) == 0
        else target_classes
    )
    gt_boxes = gt_boxes[gt_classes >= 0]

    return gt_boxes
    

def calc_ciou(pred_boxes: tf.Tensor, gt_boxes: tf.Tensor):
    """
    pred_boxes: xyxy format
    gt_boxes: xywh format
    """
    gt_boxes_xyxy = tf.stack([
        gt_boxes[:, 0],
        gt_boxes[:, 1],
        gt_boxes[:, 0] + gt_boxes[:, 2],
        gt_boxes[:, 1] + gt_boxes[:, 3],
    ], axis=1)

    ciou_matrix = compute_ciou(
        tf.expand_dims(
            tf.constant(pred_boxes, dtype=tf.float32), axis=1
        ),
        tf.expand_dims(tf.constant(gt_boxes_xyxy, dtype=tf.float32), axis=0),
        bounding_box_format="xyxy",
    ).numpy()
    
    return ciou_matrix

def count_correct_detections(
        pred_boxes,
        gt_boxes,
        iou_threshold
):
    ciou_matrix = calc_ciou(pred_boxes=pred_boxes, gt_boxes=gt_boxes)

    n_corrects = 0
    best_ciou_scores = []
    matched = set()
    for i in range(len(pred_boxes)):
        best_ciou = float(np.max(ciou_matrix[i, :]))
        best_ciou_scores.append(best_ciou)
        if best_ciou <= iou_threshold:
            continue

        # Find the GT index with max CIoU
        gt_idx = int(np.argmax(ciou_matrix[i, :]))
        if gt_idx not in matched:
            matched.add(gt_idx)
            n_corrects += 1
            
    return best_ciou_scores, n_corrects