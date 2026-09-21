from typing import Final


BOARD_SIZE: Final[int] = 9
MARKS: Final[set[str]] = {"X", "O"}

WINNING_LINES: Final[tuple[tuple[int, int, int], ...]] = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


def new_board() -> list[str | None]:
    return [None] * BOARD_SIZE


def apply_move(
    board: list[str | None],
    cell: int,
    mark: str,
) -> list[str | None]:
    if len(board) != BOARD_SIZE:
        raise ValueError("A board must contain 9 cells.")

    if not 0 <= cell < BOARD_SIZE:
        raise ValueError("Cell must be between 0 and 8.")

    if mark not in MARKS:
        raise ValueError("Mark must be X or O.")

    if board[cell] is not None:
        raise ValueError("Cell is already occupied.")

    updated_board = board.copy()
    updated_board[cell] = mark

    return updated_board


def winner(board: list[str | None]) -> str | None:
    for first, second, third in WINNING_LINES:
        mark = board[first]

        if (
            mark is not None
            and mark == board[second]
            and mark == board[third]
        ):
            return mark

    return None


def is_draw(board: list[str | None]) -> bool:
    return winner(board) is None and all(cell is not None for cell in board)


def is_finished(board: list[str | None]) -> bool:
    return winner(board) is not None or is_draw(board)


def best_move(board: list[str | None], mark: str = "O") -> int | None:
    if is_finished(board):
        return None

    available_cells = [
        index
        for index, cell in enumerate(board)
        if cell is None
    ]

    return available_cells[0] if available_cells else None