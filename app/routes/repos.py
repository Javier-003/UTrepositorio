from bson import ObjectId
import dropbox
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import base64
import requests
from app.func.func import crear_carpeta_dropbox, login_required, procesar_y_subir_multimedia_dropbox, roles_required

GITEA_URL = "http://216.238.83.143:3000/api/v1"
GITEA_WEB_URL = "http://216.238.83.143:3000"

repos_routes = Blueprint('repos', __name__)

# Obtener token del usuario logueado
def obtener_token_usuario():
    token = session.get('token')
    if not token:
        flash("Debes iniciar sesión primero")
        return None
    return token

# Listar repositorios
@repos_routes.route('/repositorios/')
@login_required
@roles_required('usuario', 'admin')
def repositorios():
    db = current_app.get_db_connection()
    username = session['user']['username']
    # Mostrar solo los repositorios del usuario en MongoDB
    repos = list(db['repositorios'].find({"usuario": username}))
    return render_template('repos.html', repos=repos)

# Crear repositorios
@repos_routes.route('/crear', methods=['POST'])
@login_required
@roles_required('usuario')
def crear():
    db = current_app.get_db_connection()

    nombre = request.form.get('nombre')
    descripcion = request.form.get('descripcion')
    fecha = request.form.get('fecha_creacion')
    estado_proyecto = request.form.get('estado')
    categoria = request.form.get('categoria')

    frameworks = request.form.getlist('frameworks[]')
    lenguajes = request.form.getlist('lenguajes[]')

    integrantes = request.form.getlist('integrantes_nombre[]')
    multimedia = request.files.getlist('multimedia[]')

    plataforma = request.form.get('plataforma')
    version_control = request.form.get('version')

    objetivos = request.form.get('objetivo')
    retos = request.form.get('retos')
    prioridad = request.form.get('prioridad')
    comentarios = request.form.get('comentarios')


    username = session['user']['username']
    token = session['user']['token']
    usuario = db['usuarios'].find_one({"username": username})
    carpeta_usuario = usuario.get('dropbox_folder_path', username)  # Usa carpeta del usuario o su nombre

    # Crear carpeta en Dropbox para este repo
    carpeta_repo_path, carpeta_repo_link = crear_carpeta_dropbox(nombre, parent_path=carpeta_usuario)
    print("Carpeta creada en Dropbox:", carpeta_repo_path, carpeta_repo_link)
    if not carpeta_repo_path:
        flash("Error creando carpeta en Dropbox")
        return redirect(url_for('repos.repositorios'))

    # Crear repositorio en Gitea
    headers = {"Authorization": f"token {token}"}
    data = {"name": nombre, "description": descripcion, "private": False}
    resp = requests.post(f"{GITEA_URL}/user/repos", headers=headers, json=data)
    if resp.status_code != 201:
        flash(f"Error creando repo en Gitea: {resp.text}")
        return redirect(url_for('repos.repositorios'))

    repo_info = resp.json()
    print("Repositorio creado en Gitea:", repo_info)

    # Guardar repo en MongoDB
    repo_doc = {
        "nombre": repo_info['name'],
        "full_name": repo_info['full_name'],
        "descripcion": repo_info['description'],
        "usuario": username,
        "integrantes": integrantes,
        "fecha_creacion": fecha,
        "categoria": categoria,
        "framework": frameworks,
        "lenguaje": lenguajes,
        "dropbox_path": carpeta_repo_path,
        "dropbox_link": carpeta_repo_link,
        "plataforma": plataforma,
        "version_control": version_control,
        "objetivos": objetivos,
        "retos": retos,
        "prioridad": prioridad,
        "comentarios": comentarios,
        "estado_proyecto": estado_proyecto,
        "estado": "pendiente"
    }
    print("Guardando en MongoDB:", repo_doc)
    insert_result = db['repositorios'].insert_one(repo_doc)

    # Subir multimedia a Dropbox
    if multimedia:
        archivos_subidos = procesar_y_subir_multimedia_dropbox(multimedia, carpeta_repo_path)
        for f in archivos_subidos:
            db['archivos'].insert_one({
                "repo_id": insert_result.inserted_id,
                "nombre": f["nombre"],
                "dropbox_path": f["path"],
                "webViewLink": f["webViewLink"]
            })

    flash("Repositorio y multimedia creados correctamente en Dropbox ✅")
    return redirect(url_for('repos.repositorios'))

# Eliminar repositorios
@repos_routes.route('/repositorios/eliminar/<nombre>', methods=['POST'])
@login_required
@roles_required('usuario')
def eliminar(nombre):
    db = current_app.get_db_connection()
    username = session['user']['username']
    token = session['user']['token']

    # Buscar el repositorio para obtener la carpeta de Dropbox
    repo = db['repositorios'].find_one({"nombre": nombre, "usuario": username})
    if repo:
        dropbox_folder_path = repo.get('dropbox_path', f"/user_{username}/{nombre}")

        # Conectar a Dropbox
        dbx = current_app.dropbox_client  # asumiendo que guardaste el cliente en Flask
        try:
            dbx.files_delete_v2(dropbox_folder_path)
            print(f"Carpeta de Dropbox eliminada: {dropbox_folder_path}")
        except Exception as e:
            print(f"Error eliminando carpeta en Dropbox: {e}")

        # Eliminar referencias de archivos asociados
        db['archivos'].delete_many({"repo_id": repo['_id']})

    # Eliminar repositorio de MongoDB
    db['repositorios'].delete_one({"nombre": nombre, "usuario": username})

    # Eliminar repositorio de Gitea
    headers = {"Authorization": f"token {token}"}
    response = requests.delete(f"{GITEA_URL}/repos/{username}/{nombre}", headers=headers)
    print(response.json() if response.content else "Repositorio eliminado en Gitea")  # debug

    flash("Repositorio y archivos asociados eliminados correctamente")
    return redirect(url_for('repos.repositorios'))

# Ver comandos de un repositorio
@repos_routes.route('/repositorios/<nombre>')
@login_required
@roles_required('usuario', 'admin')
def comandos(nombre):
    username = session['user']['username']
    token = session['user']['token']

    # URL HTTP con token para autenticación automática
    clone_url = f"http://{username}:{token}@216.238.83.143:3000/{username}/{nombre}.git"

    comandos_git = f"""# subir tu proyecto a tu repositorio "{nombre}"
git init    
git remote add origin {clone_url}
git branch -M main
git add .
git commit -m "Subida inicial del proyecto"
git push -u origin main
"""

    return render_template('repo_comandos.html', repo_name=nombre, comandos=comandos_git)

# Explorar archivos y carpetas
@repos_routes.route('/repositorios/<nombre>/archivos/', defaults={'path': ''})
@repos_routes.route('/repositorios/<nombre>/archivos/<path:path>')
@login_required
@roles_required('usuario', 'admin')
def explorar_archivos(nombre, path):
    username = session['user']['username']
    token = session['user']['token']
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


# Leer archivo de texto
@repos_routes.route('/repositorios/<repo>/archivo/<path:filepath>')
@login_required
@roles_required('usuario', 'admin')
def leer_archivo(repo, filepath):
    username = session['user']['username']
    token = session['user']['token']
    headers = {"Authorization": f"token {token}"}

    url = f"{GITEA_URL}/repos/{username}/{repo}/contents/{filepath}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        flash("No se pudo leer el archivo")
        return redirect(url_for('repos.explorar_archivos', nombre=repo))

    archivo_info = response.json()
    contenido = base64.b64decode(archivo_info['content']).decode('utf-8', errors='ignore')

    return render_template('leer_archivo.html', repo=repo, archivo=filepath, contenido=contenido)


# Visualizar todo archivo multimedia
@repos_routes.route('/informacion/<nombre>/<repo_id>')
def informacion_repo(repo_id,nombre):
    db = current_app.get_db_connection()

    # Buscar el repositorio
    repo = db['repositorios'].find_one({"_id": ObjectId(repo_id)})

    # Buscar archivos del repo
    archivos = list(db['archivos'].find({"repo_id": ObjectId(repo_id)}))

    return render_template('informacion.html', repo=repo, archivos=archivos)


