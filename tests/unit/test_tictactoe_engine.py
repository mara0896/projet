import pytest

from app.modules.tictactoe.engine import (
    apply_move,
    best_move,
    is_draw,
    new_board,
    winner,
)


def test_new_board_is_empty():
    assert new_board() == [None] * 9


def test_apply_move_returns_new_board():
    board = new_board()

    updated = apply_move(board, 4, "X")

    assert board[4] is None
    assert updated[4] == "X"


def test_winner_detects_row():
    board = [
        "X", "X", "X",
        None, "O", None,
        "O", None, None,
    ]

    assert winner(board) == "X"


def test_winner_returns_none_when_no_winner():
    board = [
        "X", "O", None,
        None, "X", None,
        None, None, "O",
    ]

    assert winner(board) is None


def test_draw_is_detected():
    board = [
        "X", "O", "X",
        "X", "O", "O",
        "O", "X", "X",
    ]

    assert is_draw(board) is True


def test_best_move_returns_empty_cell():
    board = [
        "X", "O", "X",
        None, "O", None,
        None, "X", None,
    ]

    assert best_move(board) == 3


def test_cannot_play_in_occupied_cell():
    board = new_board()
    board[0] = "X"

    with pytest.raises(ValueError):
        apply_move(board, 0, "O")