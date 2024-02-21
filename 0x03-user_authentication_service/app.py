#!/usr/bin/env python3
""" Main app file """
from flask import Flask, jsonify, request, abort, redirect
from auth import Auth

AUTH = Auth()
app = Flask(__name__)


@app.route("/", methods=["GET"], strict_slashes=False)
def hello_world():
    """Hello world route"""
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"], strict_slashes=False)
def get_users():
    """Get users route"""
    email = request.form.get("email")
    password = request.form.get("password")
    if email and password:
        try:
            AUTH.register_user(email, password)
            return jsonify({"email": email, "message": "user created"}), 200
        except ValueError:
            return jsonify({"message": "email already registered"}), 400


@app.route("/sessions", methods=["POST"], strict_slashes=False)
def login():
    """Create session route"""
    email = request.form.get("email")
    password = request.form.get("password")
    if email and password:
        if AUTH.valid_login(email, password):
            session_id = AUTH.create_session(email)
            response = jsonify({"email": email, "message": "logged in"})
            response.set_cookie("session_id", session_id)
            return response
    abort(401)


@app.route("/sessions", methods=["DELETE"], strict_slashes=False)
def logout():
    """Destroy session route"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        AUTH.destroy_session(user.id)
        return redirect("/")
    abort(403)


@app.route("/profile", methods=["GET"], strict_slashes=False)
def profile():
    """Profile route"""
    session_id = request.cookies.get("session_id")
    if not session_id:
        abort(403)
    user = AUTH.get_user_from_session_id(session_id)
    if user:
        return jsonify({"email": user.email})
    abort(403)


@app.route("/reset_password", methods=["POST"], strict_slashes=False)
def get_reset_password_token():
    """Get reset password token route"""
    email = request.form.get("email")
    if email:
        try:
            token = AUTH.get_reset_password_token(email)
            return jsonify({"email": email, "reset_token": token}), 200
        except Exception:
            abort(403)
    abort(403)


@app.route("/reset_password", methods=["PUT"], strict_slashes=False)
def update_password():
    """Update password route"""
    email = request.form.get("email")
    reset_token = request.form.get("reset_token")
    new_password = request.form.get("new_password")
    if email and reset_token and new_password:
        try:
            AUTH.update_password(reset_token, new_password)
            return jsonify({"email": email, "message": "Password updated"})
        except ValueError:
            abort(403)
    abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
