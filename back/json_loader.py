import json
import os

def load_json(file_path):
    """
    Load JSON data from file.
    file_path: relative path from the script's directory
    Returns: parsed JSON data
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, file_path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {full_path}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in file {full_path}: {e}")

# Pre-load common data
BOARD_DATA = load_json('data/board.json')
KV_DATA = load_json('data/kv.json')
CH_DATA = load_json('data/ch.json')