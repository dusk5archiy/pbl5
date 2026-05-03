def xyxy_to_xywh(xyxy_bboxes):
    xywh_bboxes = []
    for x, y, x2, y2 in xyxy_bboxes:
        w = x2 - x
        h = y2 - y
        xywh_bboxes.append([x, y, w, h])
    return xywh_bboxes

