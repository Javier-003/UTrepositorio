from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import requests
import time
from config import Config

GITEA_URL = "http://localhost:3000/api/v1"
ADMIN_TOKEN = Config.GITEA_TOKEN_ADMIN

usuarios_routes = Blueprint('usuarios', __name__)

# Registro de usuarios
@usuarios_routes.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not username or not email or not password:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for('usuarios.registro'))

        db = current_app.get_db_connection()

        if db['usuarios'].find_one({"username": username}):
            flash("El usuario ya existe.")
            return redirect(url_for('usuarios.registro'))

        # Crear usuario en Gitea como admin
        headers = {"Authorization": f"token {ADMIN_TOKEN}"}
        data = {
            "email": email,
            "username": username,
            "password": password,
            "must_change_password": False,
            "send_notify": False
        }

        resp = requests.post(f"{GITEA_URL}/admin/users", headers=headers, json=data)

        if resp.status_code == 201:
            # Guardar usuario en MongoDB sin contraseña
            db['usuarios'].insert_one({
                "username": username,
                "email": email
            })
            flash("Usuario creado. Ahora inicia sesión para generar tu token.")
            return redirect(url_for('usuarios.login'))
        else:
            flash(f"Error creando usuario: {resp.text}")

    return render_template('registro.html')


# Login de usuarios
@usuarios_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        db = current_app.get_db_connection()
        user = db['usuarios'].find_one({"username": username})

        if not user:
            flash("Usuario no encontrado. Regístrate primero.")
            return redirect(url_for('usuarios.registro'))

        # Generar un nombre de token único usando timestamp
        token_name = f"flask-session-token-{int(time.time())}"

        create_resp = requests.post(
            f"{GITEA_URL}/users/{username}/tokens",
            auth=(username, password),
            json={"name": token_name, "scopes": ["all"]}
        )

        if create_resp.status_code == 201:
            token = create_resp.json().get("sha1")
        else:
            flash(f"Error generando token: {create_resp.text}")
            return redirect(url_for('usuarios.login'))

        # Guardar token en MongoDB
        db['usuarios'].update_one(
            {"username": username},
            {"$set": {"gitea_token": token}}
        )

        # Iniciar sesión
        session['user'] = username
        session['token'] = token
        flash(f"Bienvenido {username}")
        return redirect(url_for('repos.repositorios'))

    return render_template('login.html')


# Logout de usuarios
@usuarios_routes.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('token', None)
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for('usuarios.login'))
