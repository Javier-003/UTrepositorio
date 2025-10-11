from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión primero")
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated
