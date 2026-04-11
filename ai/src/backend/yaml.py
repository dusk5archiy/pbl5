def _setup():
    import yaml

    yaml.add_representer(
        tuple,
        lambda dumper, data: dumper.represent_sequence(
            yaml.resolver.BaseResolver.DEFAULT_SEQUENCE_TAG, list(data), flow_style=True
        ),
    )
_setup()
del _setup

from yaml import * # pyright: ignore[reportWildcardImportFromLibrary]