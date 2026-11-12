"""Authentication: Microsoft Entra External ID (MSAL auth-code flow) or a local dev login."""
from functools import wraps

import msal
from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, session, url_for

from models import User, db

bp = Blueprint("auth", __name__)

ROLES = ("teacher", "student")


def _msal_app():
    cfg = current_app.config
    return msal.ConfidentialClientApplication(
        cfg["ENTRA_CLIENT_ID"], authority=cfg["ENTRA_AUTHORITY"], client_credential=cfg["ENTRA_CLIENT_SECRET"]
    )


def _role_from_claims(claims):
    # App roles "Teacher"/"Student" are defined on the app registration and assigned to users in Entra.
    roles = {r.lower() for r in claims.get("roles", [])}
    if "teacher" in roles:
        return "teacher"
    if "student" in roles:
        return "student"
    return None


def _sign_in(external_id, name, email, role):
    user = User.query.filter_by(external_id=external_id).first()
    if user is None:
        user = User(external_id=external_id, name=name, email=email, role=role)
        db.session.add(user)
    else:
        # Entra is the source of truth: role changes there take effect on next login.
        user.name, user.email, user.role = name, email, role
    db.session.commit()
    session.clear()
    session["user_id"] = user.id
    return user


@bp.before_app_request
def load_user():
    uid = session.get("user_id")
    g.user = db.session.get(User, uid) if uid else None


def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("auth.login", next=request.path))
            if role and g.user.role != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_app.config["AUTH_MODE"] == "entra":
        flow = _msal_app().initiate_auth_code_flow(scopes=[], redirect_uri=url_for("auth.callback", _external=True))
        session["auth_flow"] = flow
        return redirect(flow["auth_uri"])

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        role = request.form.get("role")
        if not name or not email or role not in ROLES:
            flash("Vui lòng nhập đủ tên, email và vai trò.", "danger")
        else:
            _sign_in(f"dev:{email}", name, email, role)
            return redirect(url_for("index"))
    return render_template("login_dev.html")


@bp.route("/auth/callback")
def callback():
    if current_app.config["AUTH_MODE"] != "entra":
        abort(404)
    try:
        result = _msal_app().acquire_token_by_auth_code_flow(session.pop("auth_flow", {}), request.args)
    except ValueError:  # state mismatch / replayed callback
        flash("Phiên đăng nhập không hợp lệ, vui lòng thử lại.", "danger")
        return redirect(url_for("index"))
    if "error" in result:
        flash(f"Đăng nhập thất bại: {result.get('error_description', result['error'])}", "danger")
        return redirect(url_for("index"))

    claims = result["id_token_claims"]
    role = _role_from_claims(claims)
    if role is None:
        return render_template("no_role.html"), 403
    email = claims.get("email") or claims.get("preferred_username") or ""
    _sign_in(claims["oid"], claims.get("name") or email, email, role)
    return redirect(url_for("index"))


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    if current_app.config["AUTH_MODE"] == "entra":
        authority = current_app.config["ENTRA_AUTHORITY"].rstrip("/")
        return redirect(
            f"{authority}/oauth2/v2.0/logout?post_logout_redirect_uri={url_for('index', _external=True)}"
        )
    return redirect(url_for("index"))
