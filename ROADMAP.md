# Mini-Games Platform — Learning Roadmap

A step-by-step build plan for a Flask website hosting several mini-games, designed so each
phase forces a specific set of topics from your training program.

**This document contains no solutions.** Code blocks illustrate a trap or a principle, never
the implementation you're meant to write.

**Budget**: 17 working days + 2 buffer. 6–8h/day.

---

## 0. The three games, and why these three

| Game | Where the logic lives | Topics it forces |
|---|---|---|
| **Tic-tac-toe vs the server** | 100% Python | Service pattern, state persistence, JSON API, AJAX, pure-function testing |
| **Guess Who? vs the server** | Python + database | Many-to-many modelling with payload, deduction engine, admin CRUD, RBAC, N+1 traps |
| **Pedantle** (already built) | Existing JS, to be re-hosted | Adopting foreign code, bulk data migration, moving secrets server-side, refactoring loose JS into components |

Three games is deliberate. **One** teaches you the stack. **Two** force you to notice what's
duplicated and extract it. **Three** tell you whether the abstraction you extracted at game two
was right or premature — and the third one being *pre-existing code you didn't write to your
own conventions* is the harshest and most realistic version of that test.

**Out of scope**: real-time multiplayer. Websockets aren't in your program and would eat two
days that Phases 4–8 need more.

### About the Pedantle specifically

It works today. It is also, right now:

- shipping its **solutions to the browser** — open devtools, read the answer;
- storing similarity data in a flat file no user account is attached to;
- unauthenticated, non-persistent (refresh = progress gone), and outside any structure.

None of that is a criticism of a static-hosted game — those were correct trade-offs for what it
was. But "make it part of a real platform" means fixing all four, and each maps onto a topic on
your list. **Do not simply copy the files into `static/` and add a link.** That's 20 minutes of
work, teaches nothing, and leaves the answers in the browser. Phase 7 is the real integration.

---

## 1. Why this ordering

Three principles govern the sequence. Understanding them matters more than the phase list,
because they tell you what to do when reality diverges from the plan.

### Principle 1 — Cost of change increases downwards

```
config / DI container   ← changing this touches every file
database schema         ← changing this needs a migration + data fix
service layer           ← changing this touches controllers + tests
controllers / templates ← changing this touches one screen
CSS                     ← changing this touches nothing
```

Build top-down. Not because it's elegant, but because a decision at the top made on day 12
costs a day of mechanical edits, while the same decision on day 1 costs nothing. That is the
*only* reason "architecture first" is worth anything — it is not about purity.

### Principle 2 — Vertical slices over horizontal layers

The wrong way:

> Day 1–3: all the models. Day 4–6: all the repositories. Day 7–9: all the services…

You get nothing runnable until day 10, discover your model is wrong on day 11, and have no
feedback in between. **Instead**: after the foundation, each phase delivers one feature
*through every layer* — entity → repository → service → DTO → mapper → controller → template →
test. It runs at the end of every phase.

### Principle 3 — Authentication early, but not first

Auth (Phase 4) lands before the games because **every game entity carries a `user_id`**. Adding
ownership afterwards means a migration, backfilling rows with no sensible owner, and rewriting
every query and test fixture. Cross-cutting concerns get retrofitted expensively.

But auth isn't Phase 1: you need one working vertical slice first to know what your
service/DTO/controller conventions actually look like. Auth is a large feature to write in a
style you haven't established yet.

### Why the finished game comes last

Integrating the Pedantle at Phase 7 rather than Phase 2 is the same principle applied to code
you already have. To absorb it you need somewhere to put it: a settled module layout, an auth
system to attach sessions to, a score module, a JS component convention, an API error format.
Integrating it on day 3 would mean inventing all of that *around a game you didn't design* —
you'd end up with the Pedantle's shape as your architecture rather than your architecture
absorbing the Pedantle.

---

## 2. Suggested project structure

Two organisational choices exist and both are defensible.

**By layer** — `app/models/`, `app/services/`, `app/repositories/`, `app/controllers/`.
**By feature** — `app/modules/guesswho/{entity,repository,service,dto,mapper,forms,controller}.py`.

I'd suggest **by feature**, with a shared `core/`. You'll spend your days working within one
game at a time, so by-feature means one open directory per session instead of six. By-layer
optimises for "change every service at once", which you'll almost never do. It also mirrors how
Odoo organises addons — one directory per functional module.

```
roadmap-project-lapi/
├── docker-compose.yml
├── .env.local              # never committed
├── .env.example            # committed, documents required keys
├── requirements.txt
├── pytest.ini
├── migrations/             # Alembic
├── data/
│   └── pedantle/           # the existing precomputed similarity files, pre-import
├── app/
│   ├── __init__.py         # create_app() — the application factory
│   ├── config.py           # env → typed config object
│   ├── container.py        # DI registrations (SINGLETON/SCOPED/TRANSIENT)
│   ├── extensions.py
│   ├── core/
│   │   ├── base_entity.py  # id, created_at, updated_at, deleted_at
│   │   ├── repository.py   # generic BaseRepository[T] w/ soft delete
│   │   ├── service.py
│   │   ├── errors.py       # domain exceptions + error handlers
│   │   └── security/
│   │       ├── hashing.py      # argon2 wrapper
│   │       ├── jwt.py
│   │       └── decorators.py   # @auth_required(roles=...)
│   ├── modules/
│   │   ├── auth/       {entity,repository,service,dto,mapper,forms,controller}.py
│   │   ├── user/
│   │   ├── tictactoe/  + engine.py   ← pure rules, zero Flask, zero DB
│   │   ├── guesswho/   + engine.py   ← pure deduction, zero Flask, zero DB
│   │   ├── pedantle/   + importer.py ← one-shot data import CLI command
│   │   └── score/      ← shared leaderboard, used by all three games
│   ├── templates/
│   │   ├── layout.html
│   │   ├── components/     # Jinja macros
│   │   └── <module>/
│   └── static/
│       ├── css/
│       └── js/
│           ├── core/api.js      # single fetch wrapper — every AJAX call goes through it
│           ├── components/      # Board, Timer, Modal, Leaderboard
│           └── games/
└── tests/
    ├── conftest.py
    ├── unit/           # services + engines, no DB
    └── integration/    # API endpoints, real test DB
```

Two structural points worth internalising:

- **`engine.py` files import neither Flask nor SQLAlchemy.** Pure functions:
  `(board, move) -> new_board`, `(characters, answers) -> remaining`. This is the highest-value
  design decision in the project — game rules testable in microseconds without a database, the
  difference between 40 fast unit tests and 40 slow flaky ones.
- **`static/js/core/api.js` exists from the first AJAX call.** One place that attaches the auth
  header, parses JSON, raises on non-2xx. The alternative is 15 copies of `fetch()` with
  slightly different error handling, and you find the divergence at the worst moment.

---

## 3. Phase-by-phase

Each phase: **goal → why now → steps → done when → traps**. Don't move on until "done when" is
genuinely true; the phases are load-bearing on each other.

---

### Phase 0 — Repository and database (0.5 day)

**Goal**: `git log` has a first commit; `psql` connects to a Postgres running in Docker.

**Why now**: you cannot make a mistake you can't undo. Git is the undo button for everything
else on this list.

**Steps**
1. `git init`, `.gitignore` (`.env.local`, `__pycache__/`, `venv/`, `.pytest_cache/`) — written
   *before* the first commit, not after.
2. GitHub repo, push. Copy the existing Pedantle files into `data/pedantle/` and a scratch
   folder now, so they're version-controlled before you start changing them.
3. `docker-compose.yml` with **only** a `postgres:16` service: named volume, port mapping, env
   from `.env.local`.
4. Virtualenv on the host. `pip install flask sqlalchemy psycopg[binary] python-dotenv`.
5. Confirm the connection with `psql` or a client.

**Done when**: `docker compose down && docker compose up -d` and your data survives. (If not,
you used an anonymous volume — find out now, not in Phase 9.)

**Traps**
- Committing `.env.local` in commit #1. A secret in git history is in git history forever.
- Skipping the named volume, then blaming Alembic for two hours.

**Habit from here on**: one branch per phase, one PR, merge when "done when" holds. Overkill for
solo work — do it anyway, because reviewing your own diff before merge catches roughly a third
of your mistakes for free.

---

### Phase 1 — Application factory, config, DI container (1.5 days)

**Goal**: `flask run` serves one page. Config from environment. A DI container resolving a
dummy service.

**Why now**: Principle 1. The container's API appears in every controller you'll ever write.
Changing `container.resolve(X)` on day 12 is a 60-file diff.

**Steps**
1. `create_app(config_name)` factory. Understand why a factory rather than a module-level
   `app = Flask(__name__)`: the factory lets tests build an app with a *different* config (test
   DB, CSRF off) in the same process. You need this in Phase 8 — build it now.
2. `config.py`: env vars into a typed object. Fail loudly at startup on a missing required key.
3. One blueprint, one template, one route. Prove the wiring.
4. The DI container. Implement three lifetimes and be able to explain them:

| Lifetime | One instance per… | Use for |
|---|---|---|
| `SINGLETON` | process | config, password hasher, JWT encoder |
| `SCOPED` | request | DB session, unit of work, current user |
| `TRANSIENT` | resolution | cheap stateless helpers |

**The bug this table exists to prevent** — a singleton capturing a scoped dependency:

```python
# BAD: UserService is a singleton, so it grabs ONE session at startup and
# holds it for the process lifetime. Request 2 gets request 1's stale,
# possibly-broken-transaction session. Symptom: intermittent
# "this session is in prepared state" errors that vanish on restart.
container.register(UserService, lifetime=SINGLETON)   # depends on Session (SCOPED)

# The rule: a component may only depend on things whose lifetime is at
# least as long as its own.
# SINGLETON -> SINGLETON only.  SCOPED -> SCOPED or SINGLETON.
```

Consider making the container *assert* that rule at registration. Twenty lines, and it converts
a class of Heisenbug into a startup crash. Learn to see that trade.

5. Bind the scoped lifetime to the request (`flask.g` or `contextvars`), cleaned up in
   `teardown_appcontext`.

**Done when**: two consecutive requests resolving a SCOPED service get different instances, two
resolutions *within* one request get the same one. Prove it with a debug route printing
`id(obj)` — then delete the route.

**Traps**
- A container with features you don't need (auto-wiring from type hints, decorator
  registration, lazy modules). You need `register(iface, impl, lifetime)` and `resolve(iface)`.
- Not disposing scoped instances at request end → pool exhaustion around request 20, which
  looks like "the database is slow".

---

### Phase 2 — Relational model, BaseEntity, migrations (1.5 days)

**Goal**: full schema on paper, `BaseEntity` implemented, first Alembic migration applied.

**Why now**: schema changes are the most expensive changes in the project. An hour on paper
saves a day of migrations.

**Steps**
1. **Design on paper first**, all three games at once: `User`, `Role`, `Game`, `GameSession`,
   `Score`; `Character`, `Attribute`, `CharacterAttribute`; `PedantleArticle`,
   `PedantleWordScore`, `PedantleGuess`. Draw relations, mark cardinalities, decide nullability.
2. Decide consciously: **one `GameSession` table for all games, or one per game?** For: shared
   leaderboard, one query for "my history", game-specific state in JSONB. Against: JSONB is
   unvalidated and can't carry foreign keys. Note that Guess Who and Pedantle both want real
   child tables (asked questions, guessed words) — which pulls toward a shared parent session
   plus per-game detail tables. Write the decision and the reason in `docs/decisions.md`; in
   three weeks you won't remember, and a mentor will ask.
3. `BaseEntity`: `id`, `created_at`, `updated_at`, `deleted_at` (nullable).
4. **Soft delete.** Understand what you're signing up for:

```python
# The trap: soft delete is opt-OUT by default, and you WILL forget.
session.query(User).filter_by(email=email).first()   # returns deleted users. Silently.

# Make the safe path the default one — a base repository whose every read
# applies the filter, so forgetting is impossible rather than merely discouraged:
class BaseRepository(Generic[T]):
    def _query(self):
        return self.session.query(self.model).filter(self.model.deleted_at.is_(None))
```

Also: what does soft delete do to **unique constraints**? A soft-deleted `user@example.com`
still occupies the unique index, so that address can never be reused. Look up partial unique
indexes (`WHERE deleted_at IS NULL`). This is the kind of detail separating "I used a pattern"
from "I understand a pattern".

5. `flask db init`, `flask db migrate`, **read the generated file**, `flask db upgrade`.

**Done when**: `flask db downgrade` then `flask db upgrade` runs clean. A migration you can't
roll back is one you can't trust.

**Traps**
- Trusting `--autogenerate`. It does not detect table renames (it drops + creates → data loss),
  some type changes, `CHECK` constraints, index renames. Read every generated migration.
- Editing an already-applied migration instead of adding a new one.
- Not committing migrations. They are source code.

---

### Phase 3 — First vertical slice: the game catalogue (2 days)

**Goal**: `/games` lists games from the database; `/admin/games` does full CRUD, through every
layer, with tests.

**Why now**: this establishes the conventions the next ten days repeat. A boring entity is the
right one to learn on — no game logic distracting you from the plumbing.

**Steps** — this order is your dependency chain:
`entity → migration → repository → service → DTO → mapper → form → controller → template → test`

1. `Game` entity: slug, name, description, thumbnail, `is_active`.
2. `GameRepository(BaseRepository[Game])`. Data access **only** — no business rules.
3. `GameService`: `find_all / find_one / insert / update / delete`. Business rules live here.
4. DTO + Mapper. The point of the layer, concretely:

```python
# BAD: the ORM entity travels all the way to the template. Consequences:
# the template can trigger lazy loads (N+1 from inside HTML, invisible in a
# Python profiler); serialising it leaks password_hash the day someone adds
# a to_dict(); every schema rename breaks templates.
return render_template("games/list.html", games=game_repo.find_all())

# GOOD: the service returns DTOs. The template sees only what the DTO exposes,
# and the DTO is a contract you change deliberately.
return render_template("games/list.html", games=game_service.find_all())
```

The mapper is the *only* place that knows how an entity becomes a DTO. Catching yourself
writing `GameDTO(...)` inside a controller is the smell.

5. WTForms `GameForm` with real validation. Server-side validation is the only validation that
   exists — HTML `required` is a UX affordance, not a check.
6. Controller: **thin**. Parse request → call service → render/redirect. An `if` about game
   rules in a controller is in the wrong file.
7. Jinja: `layout.html` + `{% macro game_card(game) %}`. Macros are your server-side component
   system; start at the first duplication, not the third.
8. **Write the tests now.** `GameService` with a mocked repository — no DB, no Flask.

**Done when**: create, list, edit and soft-delete a game in the browser, and `pytest
tests/unit` is green.

> **On testing timing** — the honest version: a stricter discipline (TDD) writes the test before
> step 3. That's genuinely better, and if you want the harder path, take it. Either way, **no
> phase from here on ends without its tests**. Phase 8 consolidates fixtures, integration
> coverage and CI — it is not the phase where testing begins. "I'll add tests at the end" is
> how projects end up with no tests, every time.

**Traps**
- Business logic in the repository (`find_active_games_for_dashboard()` is a service concern
  composed from repository primitives).
- A DTO that's a field-for-field copy of the entity — then the layer really is ceremony. A DTO
  should differ: fewer fields, flattened relations, computed values, formatted dates.

---

### Phase 4 — Authentication, JWT, RBAC (2 days)

**Goal**: register, log in, log out. Protected routes. `admin` vs `player` enforced.

**Why now**: Principle 3 — every game entity from Phase 5 on references a user.

**Steps**
1. Password hashing with **argon2** (`argon2-cffi`). Use the library's defaults; don't invent
   parameters.

```python
# BAD — all three are real bugs people ship:
hashlib.sha256(password.encode()).hexdigest()   # fast by design = brute-forceable by design
if stored_hash == incoming_hash:                # timing side-channel on comparison
    ...
hashlib.sha256((SALT + password).encode())      # one global salt = one rainbow table

# argon2's verify() handles the comparison, the per-hash salt, and the cost
# parameters. Your job is to call it and store the string it returns.
```

2. `AuthService`: `register` (uniqueness + hashing), `authenticate` (verify + generic error).
   Return the *same* message for unknown email and wrong password — a different one is a
   user-enumeration oracle.
3. JWT with PyJWT: sign, short expiry, verify. Know what a JWT is and isn't: **signed, not
   encrypted** — anyone can read the payload. Never put anything secret in the claims.
4. **Where does the token live?** Decide consciously; it's the question interviewers ask:

| Storage | XSS | CSRF | Notes |
|---|---|---|---|
| `localStorage` | any injected script reads it | immune | simplest, most common, most stolen |
| `httpOnly` cookie | JS cannot read it | needs CSRF protection | safer, more moving parts |

Either is fine for a learning project **as long as you can defend the choice and name the attack
you're exposed to**. Into `docs/decisions.md`.

5. `@auth_required(roles=("admin",))`. One decorator handling authn and authz — don't build two.
6. `Role` table, many-to-many with `User`, seeded by a migration or a CLI command.
7. Tests: expired token rejected, tampered signature rejected, wrong role → 403 (**not** 404,
   **not** 401 — know the difference: 401 "who are you", 403 "I know, and no").

**Done when**: logged-out user hitting `/admin/games` is redirected; `player` gets 403; `admin`
gets the page. All three tested.

**Traps**
- Roles as a string column on `User`. Works until a user needs two — a migration you can avoid
  by modelling the join table now.
- Checking permissions in the template (`{% if user.role == 'admin' %}`) *instead of* in the
  controller. Hiding the button is UX; the route stays open to anyone who types the URL. Do
  both, but the decorator is the one that matters.
- A JWT with no expiry: a permanent credential you can't revoke.

---

### Phase 5 — Game 1: Tic-tac-toe, server-authoritative + JSON API (2 days)

**Goal**: play a full game against a server opponent, no page reload.

**Why now**: first game and first real REST API. Auth exists, so sessions belong to a user from
the start.

**Steps**
1. **`engine.py` first, pure Python.** `apply_move`, `winner`, `is_draw`, `best_move`. Unit-test
   it immediately — the whole rule set is testable in milliseconds, and you'll write 30 cases in
   the time one DB-backed test takes to set up.
2. `GameSessionService` persists state between requests and calls the engine. Note the split:
   the engine knows the rules and nothing else; the service knows persistence and users.
3. REST endpoints. Design before writing:

```
POST   /api/tictactoe/sessions             → 201 {session_id, board, turn}
GET    /api/tictactoe/sessions/<id>        → 200 current state
POST   /api/tictactoe/sessions/<id>/moves  body {cell: 4}
                                           → 200 new state | 400 invalid | 403 not yours
```

Nouns for resources, verbs for actions, status codes for outcomes. Not
`/api/makeMove?id=3`. One consistent error envelope, registered once as a Flask error handler
rather than repeated per route.

4. **Server-authoritative means the server never trusts the request.** Validate: your session,
   your turn, cell in range, cell empty, game not already over. The client sends *intent*, the
   server decides *truth*.

```javascript
// BAD: client computes the new state and tells the server what to store.
await api.post(`/api/tictactoe/sessions/${id}/moves`, { board: newBoard, winner: "X" });
// Anyone with devtools now wins every game and writes any board they like.

// GOOD: client sends intent only; the server returns truth, the client renders it.
const state = await api.post(`/api/tictactoe/sessions/${id}/moves`, { cell: 4 });
render(state);
```

5. Front-end: `core/api.js` (build it here — it serves all three games) plus a `Board` component
   that renders a state object and emits a move event.
6. Integration tests including abuse cases: move in someone else's session, move out of turn,
   move on a finished game.

**Done when**: you can't cheat from the console. Actually try — open devtools, POST a nonsense
move, confirm 400 and unchanged stored state.

**Traps**
- Game state in the Flask session cookie instead of the DB. Breaks on a second tab, breaks on
  refresh, doesn't scale past one process, can't be replayed for a history page.
- Pickling a Python object into a column. Store JSON or a 9-char string — both inspectable in
  `psql`, and you'll want that at 2am.
- Returning HTML from `/api/*`. An API returns JSON including for errors; an HTML 500 page
  inside `response.json()` produces a client-side parse error that hides the real one.

---

### Phase 6 — Game 2: Guess Who? + reusable components (2.5 days)

**Goal**: the server secretly picks a character; you ask yes/no attribute questions, eliminate
candidates, and guess. Admins manage the character roster.

**Why now**: second pass through the pattern — this is where you *earn* your abstractions
instead of guessing them, with two concrete cases to generalise from. It's also your first real
many-to-many.

**Steps**
1. **Model the roster.** This is the phase's main modelling decision, and it's a genuine
   trade-off:

```
Option A — a column per attribute:
    character(id, name, has_glasses, has_hat, hair_color, ...)
    Fast, simple, type-safe, trivially queryable.
    Adding "wears earrings" is a migration. A second themed roster with
    different attributes doesn't fit at all.

Option B — attribute as data (EAV):
    character(id, name)
    attribute(id, code, label, value_type)
    character_attribute(character_id, attribute_id, value)
    Add attributes without a migration; multiple rosters coexist.
    Costs: no type safety, every read is a join, "characters with glasses
    AND a hat" becomes a self-join or a GROUP BY … HAVING COUNT.
```

For a fixed 24-character board, A is defensible and simpler. B is the better *exercise* and the
better fit if you ever want a second roster. Pick one, write down why, and — importantly — write
down what would make you switch. That last sentence is what senior review looks for.

2. `guesswho/engine.py`, pure Python, no DB: `answer(character, attribute) -> bool`,
   `remaining(characters, answers) -> list`, optionally `best_question(candidates)` scoring
   attributes by how evenly they split the set (information gain — a nice, self-contained
   algorithmic exercise). All unit-testable with a hand-built list of dicts.
3. Service + persistence: session holds `target_character_id` and the asked-question history.
4. **The leak to avoid**, and it's subtle here:

```python
# BAD: the endpoint that lists the board sends every character with all
# their attributes AND the session's target_id, because "the front-end
# needs the data to render". The answer is now in the network tab.
return jsonify(characters=[...], target_id=session.target_character_id)

# The client needs: the roster to draw the board, and the yes/no answer to
# each question it asked. It never needs to know which one is the target
# until the game is over. Two different DTOs of the same entity — that is
# precisely what the DTO layer is for.
```

Note this is the same class of bug the Pedantle currently has in Phase 7. Seeing it in code you
wrote yourself first makes it much easier to recognise there.

5. Endpoints: `POST /api/guesswho/sessions`, `POST …/<id>/questions {attribute_id}` → yes/no +
   remaining count, `POST …/<id>/guess {character_id}` → win/lose + reveal.
6. Admin CRUD for characters and attributes behind `@auth_required(roles=("admin",))`. This
   reuses Phase 3's pattern and Phase 4's decorator — if it doesn't *feel* like reuse, something
   in Phase 3 was built wrong, which is useful information.
7. N+1 will appear here the moment you render 24 characters with their attributes:

```python
# BAD: 1 query for characters, then 24 more when the template touches
# c.attributes. It never shows up with 3 rows of seed data.
characters = Character.query.all()

# Load what you know you need, in one query:
characters = Character.query.options(selectinload(Character.attributes)).all()
```

Turn on SQLAlchemy's `echo` for one page load and count the statements. Do this once for real —
reading about N+1 and *watching* 25 queries scroll past are different educational events.

8. **Now extract components**, with two use cases in hand:
   - Jinja macros: `card`, `pagination`, `form_field`, `flash_messages`.
   - JS: `Grid`, `Modal`, `Timer` — consistent shape (constructor takes a root element +
     options, exposes `mount()`/`destroy()`).

```javascript
// BAD: user-controlled text into innerHTML = stored XSS. A player named
// <img src=x onerror=alert(1)> runs code in every viewer's browser on the
// leaderboard page.
el.innerHTML = `<span>${player.name}</span>`;

// textContent for text, createElement for structure.
el.textContent = player.name;
```

Jinja auto-escapes. Your JS does not. Every `innerHTML` with a `${}` is a decision — make it
consciously, and note that `|safe` in a template is the same decision.

**Done when**: an admin builds a roster through the UI, a player wins a game, and no response
body anywhere reveals the target before the game ends. Check the network tab, not the code.

---

### Phase 7 — Game 3: integrating the existing Pedantle (2 days)

**Goal**: the Pedantle runs inside the platform — authenticated, persistent, on the leaderboard,
with the solutions on the server where they belong.

**Why now**: it's the counterpoint to Phases 5–6. Same platform, but you're absorbing code that
wasn't written to your conventions, and every architectural decision you made is about to be
tested by something that didn't have a vote in it.

**The framing that matters**: the temptation is to drop the files into `static/`, add a link,
and call the phase done in 20 minutes. Resist it. That leaves the answers in the browser, no
account attached, no history, no leaderboard, and teaches you nothing. The exercise is the
*absorption*, not the hosting.

**Steps**

1. **Audit first, in writing.** Before touching anything, list what the current version does and
   where each part will live afterwards. Roughly:

| Currently | Afterwards |
|---|---|
| Similarity data in a flat file | Postgres table, imported once |
| Target article in the JS | Server-side, never sent whole |
| Progress in a JS variable | `PedantleSession` + `PedantleGuess` rows |
| Global-scoped script | Component + `core/api.js` |
| Its own full HTML page | `layout.html` + a Jinja template |
| Anyone can play | `@auth_required`, session owned by a user |

Half an hour with this table saves you a day of half-migrated confusion.

2. **Import the data.** Model it as `PedantleArticle` and `PedantleWordScore(article_id, word,
   score, rank)`. Write the import as a **Flask CLI command** (`flask pedantle import <file>`),
   not a script you run once and lose — it's part of the app, it belongs in the repo, and you'll
   run it again on every fresh database. Two things to hit deliberately:

```python
# BAD: one INSERT per row. 100k words = 100k round trips = minutes.
for word, score in rows:
    db.session.add(PedantleWordScore(article_id=a.id, word=word, score=score))
    db.session.commit()          # committing inside the loop makes it worse again

# Bulk insert, one transaction. Look up bulk_insert_mappings, or COPY via
# psycopg for the genuinely large case. Then compare the timings — this is
# the clearest demonstration you'll get of why round trips dominate.
```

And the index: every guess does `WHERE article_id = ? AND word = ?`. Without a composite index
that's a sequential scan over the whole table, per guess. Add it in the migration, then use
`EXPLAIN ANALYZE` to see the plan change from `Seq Scan` to `Index Scan`. Reading about indexes
is theory; watching a query drop from 80ms to 0.2ms is not.

3. **Move the secret server-side.** This is the heart of the phase. The endpoint becomes:

```
POST /api/pedantle/sessions/<id>/guesses   body {word: "empereur"}
     → 200 {rank, score, revealed: [{pos: 12, word: "empereur"}, ...],
            progress: {found: 34, total: 210}}
```

The client sends a word and receives *only* what that word revealed. It never receives the
article text, the title, or the full word list. Note what changes: reveal logic that used to run
in the browser now runs in a service, which means it's now unit-testable — a side benefit of
moving trust boundaries that people rarely expect.

4. **Persist the session.** `PedantleSession(user_id, article_id, started_at, finished_at)` plus
   one `PedantleGuess` row per attempt. This gives you: resume after refresh, a guess history,
   duplicate-guess detection, and a real score (guess count / time) for the leaderboard. It's
   also the piece that makes the game *belong* to the platform rather than sit inside it.
5. **Refactor the front-end.** Loose globals → a component with the same shape as the Phase 6
   ones; every `fetch` → `core/api.js`; its HTML into `layout.html` with a Jinja template; its
   CSS namespaced or folded into your stylesheet. Keep the game *feel* identical — the player
   should not be able to tell. A refactor that changes behaviour isn't a refactor.
6. **Write tests for the logic you just moved.** Reveal computation, rank lookup, duplicate
   guess, unknown word, guessing after the game is finished, guessing in someone else's session.
   None of this was testable while it lived in the browser.

**Done when**: the article title appears nowhere in any network response until the game is won,
progress survives a refresh, and the Pedantle appears on the shared leaderboard alongside the
other two games.

**Traps**
- Migrating the data but leaving the answers in the JS "for now". "For now" is how it ships.
- Rewriting the game logic while moving it. Move first, verify identical behaviour, refactor
  after — two changes at once means a bug has two possible causes.
- Assuming the old data file is clean. It was built for one consumer with no validation.
  Check for duplicate words, casing inconsistencies, accents, and empty rows *during import*,
  and fail loudly — an importer that silently skips bad rows is how you get a game that's
  subtly unwinnable.

---

### Phase 8 — Test consolidation, fixtures, CI (1.5 days)

**Goal**: a suite you trust, running on every push.

**Why now**: you've written tests since Phase 3. This makes them a *system*.

**Steps**
1. `conftest.py`: `app` fixture using the Phase 1 factory with a test config; `db` fixture that
   creates the schema once and **rolls back a transaction per test** rather than dropping and
   recreating tables — orders of magnitude faster, and a fast suite is a suite you run.
2. Factory helpers for test data (`make_user(role="admin")`, `make_character(glasses=True)`).
   Plain functions with defaults and keyword overrides, not a fixture per entity.
3. Integration tests per endpoint: happy path, validation failure, unauthenticated, wrong role,
   not found.
4. Coverage as a *map*, not a target. Look at which branches are uncovered and ask whether they
   matter. 100% coverage of getters proves nothing; an uncovered `except` is a real finding.
5. GitHub Actions: install, migrate against a Postgres service container, `pytest`. Phase 0's
   Docker work now pays for itself. Include the Pedantle import in CI if the data file is small
   enough — otherwise a fixture with a handful of words.

**Done when**: green CI badge, suite under ~30s, everything passes in random order
(`pytest -p randomly`). Order-dependent tests are lying to you.

**Traps**
- Mocking SQLAlchemy. Mock the *repository interface* in unit tests; use a real database in
  integration tests. Mocked query chains test your mock, not your code.
- Tests sharing state through the database. Symptom: green individually, red together.

---

### Phase 9 — Dashboard, leaderboard, charts (1.5 days)

**Goal**: a stats page — per-game leaderboards, your history, an admin overview.

**Why now**: it needs data, and only now does data exist across three games. A dashboard built
earlier is built against imagined data.

**Steps**
1. **Aggregate in SQL, not in Python.** This is where your SQL topic actually gets exercised:

```python
# BAD: pull 50k rows over the wire to compute one number.
scores = score_repo.find_all()
avg = sum(s.value for s in scores) / len(scores)     # + ZeroDivisionError when empty

# The database is very good at this. Let it be:
#   SELECT game_id, COUNT(*), AVG(value), MAX(value)
#   FROM score WHERE deleted_at IS NULL GROUP BY game_id
```

Try a window function for ranking (`RANK() OVER (PARTITION BY game_id ORDER BY value DESC)`) —
top-N-per-group is the classic case, and doing it in Python is the classic mistake.
2. A `StatsService` returning display-shaped DTOs. Aggregates are the clearest illustration of
   why DTOs exist: there is no entity for "average score per game per week".
3. `GET /api/stats/...` returning JSON.
4. Charts with Chart.js from CDN. Rule: **the JS receives data and renders it; it computes
   nothing.** Business logic in a chart callback is unreachable by your test suite.
5. Handle the empty state. A new user's dashboard has zero rows, and "no data yet" beats a
   `ZeroDivisionError`.

Note the three games produce genuinely different score shapes — win/loss for tic-tac-toe,
questions-used for Guess Who, guesses-and-time for the Pedantle. Deciding how they share one
leaderboard (normalised score? per-game boards only?) is a real modelling question, and worth
another `docs/decisions.md` paragraph.

**Done when**: the dashboard renders correctly for a brand-new user, and each chart endpoint
issues a bounded number of queries regardless of dataset size.

---

### Phase 10 — Full dockerisation, docs, polish (1.5 days)

**Goal**: `git clone && docker compose up` gives a working app. A stranger can run it.

**Why now, not day 1**: containerising the app early means every debugging session goes through
a rebuild, and every mistake has two possible causes (your code, or the container). You'd have
paid that tax through Phases 1–9 while also learning Flask. Postgres was containerised on day 0
because you don't debug Postgres; the app is containerised now because you're done debugging it.

**Steps**
1. `Dockerfile`: multi-stage, non-root user, no dev dependencies in the final image,
   `.dockerignore` (`.git`, `venv`, `__pycache__`, `tests`, and the raw Pedantle data if it's
   large — it belongs in the DB by now, not the image).
2. `docker-compose.yml`: `web` + `db`, `depends_on` with a **healthcheck** — `depends_on` alone
   waits for the container to *start*, not for Postgres to *accept connections*, which is the
   classic first-boot crash.
3. Startup: migrations plus the Pedantle import on a fresh database. Entrypoint script or a
   documented manual step — decide and document which. "It worked on my machine because I'd
   already run it" is a real failure mode, and the import makes it much more likely here.
4. `.env.example` complete and accurate. Dev/prod differences as env vars only, never code
   branches.
5. `README.md`: what it is, screenshot, prerequisites, run instructions, test instructions,
   architecture paragraph. Someone should run this without asking you anything.
6. Final pass with `DEBUG=False`: click every page, check for 500s and stack traces leaking to
   users.

**Done when**: you delete your venv and your database volume, clone fresh into a new directory,
`docker compose up`, register an account, and play all three games.

---

### Buffer (2 days)

Not padding. Real uses: the Guess Who modelling decision needed reversing, the Pedantle data
turned out messier than expected, Alembic ate an afternoon. If you genuinely don't need them,
spend them on the optional features — never on starting a fourth game.

---

## 4. Optional features, mapped to topics

Only after Phase 10 is genuinely done. Each deepens one topic you'd otherwise touch lightly.

| Feature | Topic it deepens | Rough cost |
|---|---|---|
| **Refresh tokens + revocation** | PyJWT, security modelling. Forces "how do you invalidate a stateless token?" | 0.5d |
| **Memory game (canvas)** | The pure client-side arcade exercise dropped from the core plan; `requestAnimationFrame`, DOM state, score submission | 1d |
| **Rate limiting on guess endpoints** | Service composition, hostile-input thinking. The Pedantle is brute-forceable one word at a time — a real, non-hypothetical case | 0.5d |
| **Pedantle daily article + streaks** | Scheduled selection, date-scoped uniqueness, "one attempt per user per day" as a DB constraint rather than app code | 1d |
| **Tic-tac-toe replay from move history** | Relational modelling, engine reuse — replay is `reduce(apply_move, moves)`, which only works because the engine is pure | 1d |
| **Guess Who: server plays optimally** | Information gain / entropy scoring in the engine. Self-contained algorithmic depth, zero new infrastructure | 1d |
| **i18n (FR/EN)** | Flask-Babel, Jinja. Directly relevant — Odoo is deeply multilingual, and your Pedantle is French | 0.5d |
| **Admin audit log** | Soft delete + `created_by`, decorators, "who changed what" modelling | 0.5d |
| **Server-side pagination + filtering** | SQL (`LIMIT/OFFSET` vs keyset pagination), reusable macro, query-param DTOs | 0.5d |
| **A 4th game as a drop-in module** | The real test: can a game be added by dropping in a module with a registered blueprint and engine, touching zero existing files? | 1d |

Highest learning-per-hour: **refresh tokens** (the most commonly misunderstood concept) and
**rate limiting the Pedantle** (because it's a genuine hole in a game you actually shipped, not
an exercise).

---

## 5. Topic coverage check

| Topic | Phase |
|---|---|
| Python, business logic | 3, 5, 6, 7 |
| SQL (queries, indexes, aggregates) | 2, 7, 9 |
| SQLAlchemy ORM | 2, 3, 6, 7 |
| PostgreSQL | 0, 2, 7 |
| Relational modelling | 2, 6, 7 |
| HTML / Jinja templates | 3, 6, 7 |
| JavaScript | 5, 6, 7 |
| AJAX | 5, 6, 7 |
| YAML / ENV config | 0, 1, 10 |
| Flask | 1 onward |
| Flask-Migrate / Alembic | 2, 7 |
| Dependency injection (3 lifetimes) | 1 |
| form + DTO + mapper + service + controller + template | 3 (established), repeated 4–7 |
| DTO + Mapper | 3, 6, 9 |
| Service (CRUD) | 3 |
| Repository / BaseEntity / soft delete | 2, 3 |
| Docker / docker-compose | 0, 10 |
| WTForms / FlaskForm | 3, 4, 6 |
| JSON parsing | 5, 6, 7 |
| argon2 | 4 |
| PyJWT | 4 |
| RBAC | 4, 6 |
| `@auth_required` | 4 |
| Jinja2 (macros, inheritance) | 3, 6, 7 |
| Reusable JS components | 6, 7 |
| Charts / dashboard | 9 |
| Git / GitHub | 0 onward |
| pytest | 3 onward, consolidated in 8 |
| REST / JSON API | 5, 6, 7, 9 |

Every topic is exercised at least twice except charts — deliberate, since the patterns you'll be
asked about in a code review are the ones worth repeating.

---

## 6. Three habits, if you keep nothing else

1. **Every phase ends running and committed.** Not "nearly working". A working commit is a place
   you can return to; a half-finished branch is a place you abandon.
2. **`docs/decisions.md`, one paragraph per non-obvious choice** — what you chose, what you
   rejected, why, and what would make you change your mind. Five minutes each, and it's the
   single artefact that most convinces a reviewer you were engineering rather than assembling.
   This project has at least five: session table shape, EAV vs columns, token storage,
   Pedantle anti-cheat level, cross-game score normalisation.
3. **When you're about to add an abstraction, count your use cases.** One is a guess. Two is a
   pattern. The interface, the base class, the config flag for a value that never changes — they
   cost more to maintain than the duplication they remove, until the third time. Deleted code
   has no bugs.
