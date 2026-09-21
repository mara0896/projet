from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from ...container import Container
from ...core.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
)
from .forms import LoginForm, RegisterForm


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth",
)


def _container() -> Container:
    return current_app.extensions["container"]


def _auth_service():
    return _container().resolve("auth_service")


def _jwt_service():
    return _container().resolve("jwt_service")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        try:
            _auth_service().register(
                email=form.email.data,
                password=form.password.data,
                display_name=form.display_name.data,
            )
        except EmailAlreadyRegistered:
            form.email.errors.append(
                "An account already uses this email."
            )
        else:
            flash(
                "Registration successful. Please log in.",
                "success",
            )
            return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html",
        form=form,
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = _auth_service().authenticate(
                email=form.email.data,
                password=form.password.data,
            )
        except InvalidCredentials:
            form.email.errors.append(
                "Invalid email or password."
            )
        else:
            token = _jwt_service().create_token(user.id)

            response = redirect(
                request.args.get(
                    "next",
                    url_for("main.home"),
                )
            )

            response.set_cookie(
                "access_token",
                token,
                httponly=True,
                secure=False,
                samesite="Lax",
                max_age=(
                    _jwt_service().expires_minutes * 60
                ),
            )

            return response

    return render_template(
        "auth/login.html",
        form=form,
    )

@auth_bp.post("/logout")
def logout():
    response = redirect(url_for("main.home"))
    response.delete_cookie("access_token")
    return response
