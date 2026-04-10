import yaml

yaml.add_representer(
    tuple,
    lambda dumper, data: dumper.represent_sequence(
        yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, list(data), flow_style=True
    ),
)