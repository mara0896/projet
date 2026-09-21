from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from ...core.security.decorators import auth_required

from ...container import Container
from ...core.errors import GameSlugAlreadyExists
from .forms import GameForm
from .mapper import GameMapper


admin_game_bp = Blueprint(
    "admin_games",
    __name__,
    url_prefix="/admin/games",
)


def _service():
    container: Container = current_app.extensions["container"]
    return container.resolve("game_service")


@admin_game_bp.get("")
@auth_required(roles=("admin",))
def list_admin_games():
    games = _service().find_all_games()
    game_dtos = [GameMapper.to_admin(game) for game in games]

    return render_template(
        "admin/games/list.html",
        games=game_dtos,
    )


@admin_game_bp.route("/new", methods=["GET", "POST"])
@auth_required(roles=("admin",))
def create_game():
    form = GameForm()

    if form.validate_on_submit():
        try:
            _service().create({
                "slug": form.slug.data,
                "name": form.name.data,
                "description": form.description.data,
                "thumbnail": form.thumbnail.data,
                "is_active": form.is_active.data,
            })
        except GameSlugAlreadyExists:
            form.slug.errors.append("This slug is already in use.")
        else:
            flash("Game created.", "success")
            return redirect(url_for("admin_games.list_admin_games"))

    return render_template(
        "admin/games/form.html",
        form=form,
        title="Create game",
    )


@admin_game_bp.route("/<int:game_id>/edit", methods=["GET", "POST"])
@auth_required(roles=("admin",))
def edit_game(game_id: int):
    service = _service()
    game = service.find_one(game_id)

    form = GameForm(obj=game)

    if form.validate_on_submit():
        service.update(
            game_id,
            {
                "slug": form.slug.data,
                "name": form.name.data,
                "description": form.description.data,
                "thumbnail": form.thumbnail.data,
                "is_active": form.is_active.data,
            },
        )

        flash("Game updated.", "success")
        return redirect(url_for("admin_games.list_admin_games"))

    return render_template(
        "admin/games/form.html",
        form=form,
        title="Edit game",
    )


@admin_game_bp.post("/<int:game_id>/delete")
@auth_required(roles=("admin",))
def delete_game(game_id: int):
    _service().delete(game_id)

    flash("Game deleted.", "success")
    return redirect(url_for("admin_games.list_admin_games"))
