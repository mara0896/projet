import { get, post } from "../core/api.js";

const boardElement = document.querySelector("#board");
const messageElement = document.querySelector("#message");

let sessionId = null;

function render(state) {
  boardElement.innerHTML = "";

  state.board.forEach((mark, cell) => {
    const button = document.createElement("button");

    button.type = "button";
    button.textContent = mark || "";
    button.dataset.cell = cell;

    button.addEventListener("click", () => {
      play(cell);
    });

    boardElement.appendChild(button);
  });

  if (state.winner) {
    messageElement.textContent = `${state.winner} wins`;
  } else if (state.status === "finished") {
    messageElement.textContent = "Draw";
  } else {
    messageElement.textContent = `Turn: ${state.turn}`;
  }
}

async function startGame() {
  const state = await post("/api/tictactoe/sessions", {});

  sessionId = state.session_id;
  render(state);
}

async function play(cell) {
  try {
    const state = await post(`/api/tictactoe/sessions/${sessionId}/moves`, {
      cell,
    });

    render(state);
  } catch (error) {
    messageElement.textContent = error.message;
  }
}

document.querySelector("#new-game").addEventListener("click", startGame);

startGame();
