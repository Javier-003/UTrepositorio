from functools import wraps
import os
import uuid
import dropbox
from dropbox.files import WriteMode
from flask import current_app, session, redirect, url_for, flash
#from googleapiclient.http import MediaFileUpload
DROPBOX_ACCESS_TOKEN = current_app.config['DROPBOX_ACCESS_TOKEN']

dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión primero")
            return redirect(url_for('usuarios.login'))
        return f(*args, **kwargs)
    return decorated

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = session.get('user')
            if not user:
                flash("Debes iniciar sesión primero")
                return redirect(url_for('usuarios.login'))

            if user.get('role') not in roles:
                flash("No tienes permiso para acceder a esta página")
                return redirect(url_for('main.index'))
            return f(*args, **kwargs)
        return decorated
    return wrapper

def crear_carpeta_dropbox(nombre_carpeta, parent_path=""):
    """
    Crea una carpeta en Dropbox. Retorna (path, link_compartido)
    """
    try:
        carpeta_path = f"/{parent_path}/{nombre_carpeta}".replace("//", "/")
        dbx.files_create_folder_v2(carpeta_path)
        # Crear un enlace compartido
        shared_link = dbx.sharing_create_shared_link_with_settings(carpeta_path).url
        return carpeta_path, shared_link
    except dropbox.exceptions.ApiError as e:
        print("❌ Error creando carpeta en Dropbox:", e)
        return None, None


def subir_archivo_dropbox(archivo, carpeta_path):
    """
    Sube un archivo a Dropbox y retorna info básica
    """
    try:
        nombre_archivo = archivo.filename
        ruta_destino = f"{carpeta_path}/{nombre_archivo}"
        dbx.files_upload(archivo.read(), ruta_destino, mode=WriteMode("overwrite"))
        link = dbx.sharing_create_shared_link_with_settings(ruta_destino).url
        link_directo = link.replace("?dl=0", "?raw=1")
        return {
            "nombre": nombre_archivo,
            "path": ruta_destino,
            "webViewLink": link_directo
        }
    except Exception as e:
        print(f"❌ Error subiendo archivo {archivo.filename}: {e}")
        return None


def procesar_y_subir_multimedia_dropbox(multimedia, carpeta_path):
    archivos_subidos = []
    for archivo in multimedia:
        result = subir_archivo_dropbox(archivo, carpeta_path)
        if result:
            archivos_subidos.append(result)
    return archivos_subidos


