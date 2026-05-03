import os

def split_path(filepath: str, default_ext: str):
    dirname = os.path.dirname(filepath)
    basename, ext = os.path.splitext(os.path.basename(filepath))
    model_extension = ext[1:] if ext else default_ext

    return dirname, basename, model_extension
