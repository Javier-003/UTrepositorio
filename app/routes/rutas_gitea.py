from flask import Blueprint, jsonify, request
import requests
from config import Config

gitea_routes = Blueprint('gitea', __name__)

GITEA_URL = "http://216.238.83.143:3000/api/v1"

ADMIN_TOKEN = Config.GITEA_TOKEN_ADMIN 

@gitea_routes.route("/api/buscar_usuario", methods=["GET"])
def buscar_usuario():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    headers = {"Authorization": f"token {ADMIN_TOKEN}"}
    response = requests.get(f"{GITEA_URL}/users/search", headers=headers, params={"q": q, "limit": 10})

    if response.status_code == 200:
        data = response.json()
        resultados = [
            {
                "username": u["login"],
                "nombre": u.get("full_name") or u["login"]
            }
            for u in data.get("data", [])
        ]
        return jsonify(resultados)
    else:
        return jsonify([]), 500
