import tensorflow as tf

class Task(tf.keras.Model):
    """Base class for Task models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backbone = None
        self._functional_layer_ids = set(
            id(layer) for layer in self._flatten_layers()
        )

    @property
    def backbone(self):
        """A `keras.Model` instance providing the backbone submodel."""
        return self._backbone

    @backbone.setter
    def backbone(self, value):
        self._backbone = value

    def get_config(self):
        # Don't chain to super here. The default `get_config()` for functional
        # models is nested and cannot be passed to our Task constructors.
        return {
            "name": self.name,
            "trainable": self.trainable,
        }

    @classmethod
    def from_config(cls, config):
        # The default `from_config()` for functional models will return a
        # vanilla `keras.Model`. We override it to get a subclass instance back.
        if "backbone" in config and isinstance(config["backbone"], dict):
            config["backbone"] = tf.keras.layers.deserialize(config["backbone"])
        return cls(**config)

    @property
    def layers(self):
        # Some of our task models don't use the Backbone directly, but create
        # a feature extractor from it. In these cases, we don't want to count
        # the `backbone` as a layer, because it will be included in the model
        # summary and saves weights despite not being part of the model graph.
        layers = super().layers
        if hasattr(self, "backbone") and self.backbone in layers:
            # We know that the backbone is not part of the graph if it has no
            # inbound nodes.
            if len(self.backbone._inbound_nodes) == 0:
                layers.remove(self.backbone)
        return layers

    def __setattr__(self, name, value):
        # Work around torch setattr for properties.
        if name in ["backbone"]:
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)