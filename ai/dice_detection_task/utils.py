import tensorflow as tf


# Function to decode DFL distributions
def decode_dfl(dfl_logits, img_height=480, img_width=640):
    # dfl_logits shape: (num_anchors, 64)
    # 64 = 4 coordinates * 16 bins per coordinate
    batch_size = tf.shape(dfl_logits)[0]

    # Reshape to (num_anchors, 4, 16)
    dfl_reshaped = tf.reshape(dfl_logits, [batch_size, 4, 16])

    # Apply softmax to get probabilities for each bin
    dfl_softmax = tf.nn.softmax(dfl_reshaped, axis=-1)

    # Create projection matrix (0, 1, 2, ..., 15)
    proj = tf.cast(tf.range(16), tf.float32)

    # Compute expected value for each coordinate
    decoded = tf.reduce_sum(dfl_softmax * proj, axis=-1)

    # Convert from relative offsets to actual coordinates
    # Typical YOLO models use a stride-based approach
    # For 6300 anchors on 640x480 image, estimate stride and anchor grid

    # Create anchor grid (simplified approach)
    # Assuming 3 scales with strides [8, 16, 32]
    strides = [8, 16, 32]
    anchor_points = []

    for stride in strides:
        h_grid = img_height // stride
        w_grid = img_width // stride

        # Create grid coordinates
        y_coords = tf.range(h_grid, dtype=tf.float32) + 0.5
        x_coords = tf.range(w_grid, dtype=tf.float32) + 0.5

        grid_y, grid_x = tf.meshgrid(y_coords, x_coords, indexing="ij")

        # Flatten and scale by stride
        grid_points = tf.stack(
            [tf.reshape(grid_x, [-1]) * stride, tf.reshape(grid_y, [-1]) * stride],
            axis=1,
        )

        anchor_points.append(grid_points)

    # Concatenate all anchor points
    all_anchors = tf.concat(anchor_points, axis=0)

    # Ensure we have the right number of anchors
    num_anchors = tf.shape(decoded)[0]
    all_anchors = all_anchors[:num_anchors]

    # Convert DFL output to bbox format
    # decoded[:, 0:2] are left, top offsets
    # decoded[:, 2:4] are right, bottom offsets

    # Scale the offsets (DFL typically uses stride as scale factor)
    stride_scale = 8.0  # Use minimum stride as base scale

    x1 = all_anchors[:, 0] - decoded[:, 0] * stride_scale
    y1 = all_anchors[:, 1] - decoded[:, 1] * stride_scale
    x2 = all_anchors[:, 0] + decoded[:, 2] * stride_scale
    y2 = all_anchors[:, 1] + decoded[:, 3] * stride_scale

    # Stack to get final bounding boxes
    bbox_coords = tf.stack([x1, y1, x2, y2], axis=1)

    return bbox_coords
