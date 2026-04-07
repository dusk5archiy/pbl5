import tensorflow as tf

def scale_loss_for_distribution(loss_value):
    """Scales and returns the given loss value by the number of replicas."""
    num_replicas = tf.distribute.get_strategy().num_replicas_in_sync
    if num_replicas > 1:
        loss_value *= 1.0 / num_replicas
    return loss_value


def get_feature_extractor(model, layer_names, output_keys=None):
    if not output_keys:
        output_keys = layer_names
    items = zip(output_keys, layer_names)
    outputs = {key: model.get_layer(name).output for key, name in items}
    return tf.keras.Model(inputs=model.inputs, outputs=outputs)

