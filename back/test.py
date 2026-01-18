from game_init import init_game_state
from game_logic import move_with_dice_path
from game_model import GameState, GameStatePlayer


def test_init_game_state_success():
    """Test successful game state initialization"""
    players = ["red", "blue", "green"]

    game_state = init_game_state(players)

    # Validate game state structure
    assert isinstance(game_state.kv_queue, list)
    assert isinstance(game_state.ch_queue, list)
    assert isinstance(game_state.bds, dict)
    assert isinstance(game_state.cards, dict)
    assert game_state.player_queue == ["red", "blue", "green"]
    assert game_state.current_player == "red"
    assert game_state.double_roll_stack == 0

    # Validate players
    players_dict = game_state.players
    assert "red" in players_dict
    assert "blue" in players_dict
    assert "green" in players_dict

    for _, player_data in players_dict.items():
        assert isinstance(player_data, GameStatePlayer)
        assert player_data.budget == 1500
        assert player_data.at == "BDAU"

    print("✓ test_init_game_state_success passed")


def test_init_game_state_empty_players():
    """Test game state initialization with empty player list"""
    players = []

    game_state = init_game_state(players)

    # Should still return a game state
    assert isinstance(game_state, GameState)
    assert game_state.player_queue == []
    assert game_state.current_player == ""

    print("✓ test_init_game_state_empty_players passed")


def test_move_with_dice_path_success():
    """Test successful path calculation"""
    current_pos = "BDAU"
    steps = 7

    path = move_with_dice_path(current_pos, steps)

    # Validate path is a list of strings
    assert isinstance(path, list)
    assert len(path) == steps + 1  # +1 because it includes starting position
    assert all(isinstance(pos, str) for pos in path)

    # First position should be current position
    assert path[0] == current_pos

    # Last position should be 7 steps away
    assert path[-1] != current_pos

    print("✓ test_move_with_dice_path_success passed")


def test_move_with_dice_path_edge_cases():
    """Test path calculation with edge cases"""
    # Test with 0 steps
    path = move_with_dice_path("BDAU", 0)
    assert len(path) == 1
    assert path[0] == "BDAU"

    # Test with large steps (should wrap around)
    path = move_with_dice_path("BDAU", 100)
    assert len(path) == 101  # 100 steps + start
    assert path[0] == "BDAU"

    print("✓ test_move_with_dice_path_edge_cases passed")


def test_game_state_integrity():
    """Test that game state operations maintain integrity"""
    # Initialize game
    players = ["red", "blue"]
    game_state = init_game_state(players)

    # Store original state for comparison
    original_player_queue = game_state.player_queue.copy()
    original_players = {k: v for k, v in game_state.players.items()}

    # Simulate dice roll and movement
    current_player = game_state.current_player
    current_pos = game_state.players[current_player].at
    steps = 5

    path = move_with_dice_path(current_pos, steps)
    new_pos = path[-1]

    # Update game state (simulate what API would do)
    game_state.players[current_player].at = new_pos

    # Switch to next player
    player_queue = game_state.player_queue
    current_index = player_queue.index(current_player)
    next_index = (current_index + 1) % len(player_queue)
    game_state.current_player = player_queue[next_index]

    # Check that core structure is maintained
    assert game_state.player_queue == original_player_queue
    assert set(game_state.players.keys()) == set(original_players.keys())

    # Check that budgets are unchanged
    for player_id in original_players:
        assert (
            game_state.players[player_id].budget == original_players[player_id].budget
        )

    # Check that position was updated
    assert game_state.players["red"].at == new_pos
    # Check that current player changed
    assert game_state.current_player == "blue"

    print("✓ test_game_state_integrity passed")


def test_player_rotation():
    """Test player rotation logic"""
    players = ["red", "blue", "green"]
    game_state = init_game_state(players)

    # Initial state
    assert game_state.current_player == "red"

    # Rotate players manually
    for expected_player in ["blue", "green", "red", "blue"]:
        player_queue = game_state.player_queue
        current_player = game_state.current_player
        current_index = player_queue.index(current_player)
        next_index = (current_index + 1) % len(player_queue)
        game_state.current_player = player_queue[next_index]

        assert game_state.current_player == expected_player

    print("✓ test_player_rotation passed")


def run_all_tests():
    """Run all test functions"""
    print("Running Monopoly backend tests...\n")

    try:
        test_init_game_state_success()
        test_init_game_state_empty_players()
        test_move_with_dice_path_success()
        test_move_with_dice_path_edge_cases()
        test_game_state_integrity()
        test_player_rotation()

        print("\n✅ All tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_tests()
