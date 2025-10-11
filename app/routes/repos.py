from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import base64
import requests
from app.func.func import login_required

GITEA_URL = "http://localhost:3000/api/v1"

repos_routes = Blueprint('repos', __name__)

# Obtener token del usuario logueado
def obtener_token_usuario():
    token = session.get('token')
    if not token:
        flash("Debes iniciar sesión primero")
        return None
    return token

# ------------------------------
# 🔹 LISTAR REPOSITORIOS
# ------------------------------
@repos_routes.route('/repositorios/')
@login_required
def repositorios():
    db = current_app.get_db_connection()
    username = session['user']

    # Mostrar solo los repositorios del usuario en MongoDB
    repos = list(db['repositorios'].find({"usuario": username}))
    return render_template('repos.html', repos=repos)

# ------------------------------
# 🔹 CREAR REPOSITORIO
# ------------------------------
@repos_routes.route('/crear', methods=['POST'])
@login_required
def crear():
    db = current_app.get_db_connection()
    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    username = session['user']
    token = session.get('token')

    if nombre:
        # Guardar en MongoDB
        db['repositorios'].insert_one({
            "nombre": nombre,
            "descripcion": descripcion,
            "usuario": username
        })

        # Crear repositorio en Gitea
        headers = {"Authorization": f"token {token}"}
        data = {"name": nombre, "description": descripcion, "private": False}
        response = requests.post(f"{GITEA_URL}/user/repos", headers=headers, json=data)
        print(response.json() if response.content else "Repositorio creado en Gitea")  # debug

    return redirect(url_for('repos.repositorios'))

# ------------------------------
# 🔹 ELIMINAR REPOSITORIO
# ------------------------------
@repos_routes.route('/repositorios/eliminar/<nombre>', methods=['POST'])
@login_required
def eliminar(nombre):
    db = current_app.get_db_connection()
    username = session['user']
    token = session.get('token')

    # Eliminar de MongoDB solo si pertenece al usuario
    db['repositorios'].delete_one({"nombre": nombre, "usuario": username})

    # Eliminar de Gitea
    headers = {"Authorization": f"token {token}"}
    response = requests.delete(f"{GITEA_URL}/repos/{username}/{nombre}", headers=headers)
    print(response.json() if response.content else "Repositorio eliminado en Gitea")  # debug

    return redirect(url_for('repos.repositorios'))

# ------------------------------
# 🔹 VER COMANDOS DE UN REPOSITORIO
# ------------------------------
@repos_routes.route('/repositorios/<nombre>')
@login_required
def comandos(nombre):
    username = session['user']
    token = session.get('token')

    # URL HTTP con token para autenticación automática
    clone_url = f"http://localhost:3000/{username}/{nombre}.git"

    comandos_git = f"""# Clonar el repositorio
git clone {clone_url}

# Entrar al repositorio
cd {nombre}

# Agregar cambios y subir
git add .
git commit -m "mensaje"
git push origin main
"""

    return render_template('repo_comandos.html', repo_name=nombre, comandos=comandos_git)


# ------------------------------
# 🔹 EXPLORAR ARCHIVOS / CARPETAS
# ------------------------------
@repos_routes.route('/repositorios/<nombre>/archivos/', defaults={'path': ''})
@repos_routes.route('/repositorios/<nombre>/archivos/<path:path>')
@login_required
def explorar_archivos(nombre, path):
    username = session['user']
    token = session.get('token')
    headers = {"Authorization": f"token {token}"}

    url = f"{GITEA_URL}/repos/{username}/{nombre}/contents/{path}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        flash("No se pudieron obtener los archivos")
        return redirect(url_for('repos.repositorios'))

    archivos = response.json()
    # archivos puede ser dict si path es archivo, list si path es carpeta
    if isinstance(archivos, dict) and archivos.get('type') == 'file':
        # Si es un archivo, redirigir a leer_archivo
        return redirect(url_for('repos.leer_archivo', repo=nombre, filepath=path))

    return render_template('archivos.html', repo=nombre, archivos=archivos, path=path)


# ------------------------------
# 🔹 LEER ARCHIVO DE TEXTO
# ------------------------------
@repos_routes.route('/repositorios/<repo>/archivo/<path:filepath>')
@login_required
def leer_archivo(repo, filepath):
    username = session['user']
    token = session.get('token')
    headers = {"Authorization": f"token {token}"}

    url = f"{GITEA_URL}/repos/{username}/{repo}/contents/{filepath}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        flash("No se pudo leer el archivo")
        return redirect(url_for('repos.explorar_archivos', nombre=repo))

    archivo_info = response.json()
    contenido = base64.b64decode(archivo_info['content']).decode('utf-8', errors='ignore')

    return render_template('leer_archivo.html', repo=repo, archivo=filepath, contenido=contenido)