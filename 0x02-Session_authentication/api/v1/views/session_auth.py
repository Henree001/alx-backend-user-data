#!/usr/bin/env python3
"""Routes for the Session authentication."""
from api.v1.views import app_views
from flask import jsonify, request, session, abort
from models.user import User
import os


@app_views.route("/auth_session/login", methods=["POST"], strict_slashes=False)
def login():
    """Login session"""
    email = request.form.get("email")
    password = request.form.get("password")
    if email is None:
        return jsonify({"error": "email missing"}), 400
    if password is None:
        return jsonify({"error": "password missing"}), 400
    try:
        user = User.search({"email": email})
    except Exception:
        return None
    if len(user) == 0 or user is None:
        return jsonify({"error": "no user found for this email"}), 404
    if not user[0].is_valid_password(password):
        return jsonify({"error": "wrong password"}), 401
    from api.v1.app import auth

    session_id = auth.create_session(user[0].id)
    # session[os.getenv("SESSION_NAME")] = session_id
    response = jsonify(user[0].to_json())
    response.set_cookie(os.getenv("SESSION_NAME"), session_id)
    return response


@app_views.route(
    "/api/v1/auth_session/logout", methods=["DELETE"], strict_slashes=False
)
def logout():
    """Log outs a user and deletes user session"""
    from api.v1.app import auth

    delete = auth.destroy_session(request)
    if not delete:
        abort(404)
    return jsonify({}), 200
