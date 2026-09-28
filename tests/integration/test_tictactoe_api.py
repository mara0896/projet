# Test main move behaviors :
# - legal move - accepted - saved
# out of range - rejected
# occupied cell - rejected
# one player can't move anymore - reject additional moves
# the game is finished - reject additional moves


from app.extensions import db
from app.models import GameSession


CREATE_SESSION_URL = "/api/tictactoe/sessions"


def start_session(client):
    response = client.post(CREATE_SESSION_URL, json={})
    assert response.status_code == 201
    return response.get_json()["session_id"]


def test_valid_move_updates_and_persists_board(
    app,
    logged_in_client,
):
    session_id = start_session(logged_in_client)

    response = logged_in_client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 4},
    )

    assert response.status_code == 200
    returned_state = response.get_json()
    assert returned_state["board"][4] == "X"

    # Read it again through the GET endpoint to verify persistence.
    read_response = logged_in_client.get(
        f"/api/tictactoe/sessions/{session_id}"
    )

    assert read_response.status_code == 200
    saved_state = read_response.get_json()
    assert saved_state["board"] == returned_state["board"]


def test_out_of_range_move_is_rejected_without_changing_board(
    logged_in_client,
):
    session_id = start_session(logged_in_client)

    response = logged_in_client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 99},
    )

    assert response.status_code == 400

    read_response = logged_in_client.get(
        f"/api/tictactoe/sessions/{session_id}"
    )

    assert read_response.status_code == 200
    assert read_response.get_json()["board"] == [None] * 9


def test_occupied_cell_move_is_rejected(
    logged_in_client,
):
    session_id = start_session(logged_in_client)

    first_move = logged_in_client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 4},
    )
    assert first_move.status_code == 200
    board_after_first_move = first_move.get_json()["board"]

    second_move = logged_in_client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 4},
    )

    assert second_move.status_code == 400

    read_response = logged_in_client.get(
        f"/api/tictactoe/sessions/{session_id}"
    )
    assert read_response.get_json()["board"] == board_after_first_move


def test_another_user_cannot_move_in_this_users_session(
    client,
    game_data,
):
    client.set_cookie("access_token", game_data["owner_token"])
    session_id = start_session(client)

    # Change the test client's identity to the other user.
    client.set_cookie("access_token", game_data["other_token"])

    response = client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 4},
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Not your session"


def test_finished_game_rejects_further_moves(
    app,
    logged_in_client,
):
    session_id = start_session(logged_in_client)

    # Arrange a board where X can win by playing cell 2.
    with app.app_context():
        game_session = db.session.get(GameSession, session_id)
        game_session.state = {
            "board": [
                "X", "X", None,
                "O", "O", None,
                None, None, None,
            ],
            "turn": "X",
            "winner": None,
        }
        db.session.commit()

    winning_move = logged_in_client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 2},
    )

    assert winning_move.status_code == 200
    assert winning_move.get_json()["winner"] == "X"
    assert winning_move.get_json()["status"] == "finished"

    later_move = logged_in_client.post(
        f"/api/tictactoe/sessions/{session_id}/moves",
        json={"cell": 5},
    )

    assert later_move.status_code == 400
