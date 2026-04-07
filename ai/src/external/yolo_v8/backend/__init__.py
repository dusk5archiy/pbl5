from . import config  # noqa: E402

def assert_tf_keras(src):
    if config.keras_3():
        raise NotImplementedError(
            f"KerasCV component {src} does not yet support Keras 3, and can "
            "only be used in `tf.keras`."
        )


def supports_ragged():
    return not config.keras_3()
