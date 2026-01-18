import json
import os
from json_loader import load_json, BOARD_DATA

def get_position_index(position_symbol, board=BOARD_DATA):
    """Convert position symbol to index"""
    try:
        return board.index(position_symbol)
    except ValueError:
        raise ValueError(f"Position symbol '{position_symbol}' not found in board")

def get_steps_path(current_position_symbol, step):
    """
    Tính đường đi từng bước sau khi thảy xúc xắc và trả về list các ký hiệu ô.
    current_position_symbol: ký hiệu ô hiện tại (string)
    step: số bước từ xúc xắc
    Trả về: list các ký hiệu ô từ vị trí hiện tại đến vị trí mới
    """
    board = BOARD_DATA
    current_position = get_position_index(current_position_symbol, board)
    board_size = len(board)
    path = []
    for i in range(step + 1):
        pos = (current_position + i) % board_size
        path.append(board[pos])
    return path
