import dropbox
from flask import Flask, g
from pymongo import MongoClient
import certifi
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    ca = certifi.where()

    # Conexión a MongoDB
    def get_db_connection():
        if 'db' not in g:
            try:
                client = MongoClient(Config.MONGO_URI)
                g.db = client[Config.DATABASE_NAME]
            except Exception as e:
                print(f"Error de conexión con la base de datos: {e}")
                g.db = None
        return g.db
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGHosi2vfUFVohfhjSn1NAQzJyN3tlBjWWBV8GMtpCBI7yswby9yV6M-FRiXDvSWCcfI6bfjsksP6dbsT9JaPDpBad2AtHy8o3QSR2Y8d_kgkiPsGl-ibooJxIj75x_NG6rFsm8NU_NCY2tezAFPmfEZv53xBZbu-4a2wn5DyqHIbFTz5kTiWYy8JyxupZZuc9QWHs7bTQBWhoDbK0BTx8CmUhXGZ6ZCRvwK4gDfQKILutZXu_d5-oTL3Dsgqj6BEeTltTJja5IF7liVNeaai-8RJXtIbtB7OZPupAbilJNZ076rnQxhIdFUVrgf9qDRwR3gx4Mv1C_rwAPJLWcx9m1l3GBDYY6Zs7KGFyYkbQVQMj0VzGeVRpNqaOAcSgMsqhrq4cQBmTWB7pWFMJwuAZ2SCReoxR3iJghdIck3rKyAfP_VbKCIaC7IR6OcRK3VqTSVtibd8IaVkNiJWov7nix5TcfdMDQkjUHCrFpl5UdkWxsrcpxhkwHqnY06C1HsPc8WXy1eQNM2tMqQez4GtH2O277VSEILEV-NcFuQJ9ocXwjqC5y-VTZf1o9uOvVDXl_dY5FgGiFvWRb_hupW1-Ehq5wtwdqYoOdzTkmziOZBx6Ygs2pZ1NGcuECHIuJsFn9TfSVhoDOb4kSq3vu8rFqM-0V0jbOxtNGWMY0apqYKz4-Beh4K1wKXdIp9St_YTgP5twmqbFzRWigc4K3iUkBwH2vsW2JQXGnzvQP2j9igrs3SgyUC9Oz7H74abDKo7fQ1_WrFY46GhxOYm-1Fd9ZT1GRuDK-RqnSALO7nxNapUAMr08XR9laMpc7FDwP9XLVLuuvqDQRSJZ0JKE0lsM3V0MhJYnDZrJQ8Z0zxQploFCJVWXbxTDI216DX-lcF8ZygKkhhWKcTtmFbyEocJtJM_S6a91yo2KYbBYDtfqcBcKGHNFbRvTVI7vzJqXXVAHNQVHDZ2qLLN-03gVR_nkovJaAUAl5okTl6uL8RCFeHHtpzFNo7B6gU9O2BWxyAt1cl89Z2JykSlojU9ubUjCPy4IGfvSJkqK43Qv7UAHygb_KxgM5nBWojvSs4jZXUh8y-YsmzoJlGMb633jGUWCo2b9ww2o9m2sHPwOmkAz-lprxNl-GmvQb70oUTBNhrnaezKLa_PXDkFcAxsgLr_OlMMuw4wZhSzyhZnZ06kuujVKjpH8nsW_80x5hvfG7VcjwG-_FKBE2BCxmgJ_nj4dNS-_OMXF1e44gyI0mAigKe8fQ97n1atqbMs-ofjRrHbk1VQR8-Up26_i3c8XBHSwV4p_c0zeZJJmEJL6wYRbpc6FRyw4tuo5YyF1bx5eM3USwmuKTYCS7XFpNAz9UyIhdhYYKKrYqoFBNPLF-jcET_I0uiKoWy-xBd8VMxshwQUoXwBBHcK-NGM74h8_BGgHXHL81wobw6zIOzUdVpOQWbmiOBbnrku7Ltay0gLMONc-o"
    app.dropbox_client = dropbox.Dropbox(app.config["DROPBOX_ACCESS_TOKEN"])

    @app.teardown_appcontext
    def close_db_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            try:
                client = db.client
                client.close()
            except Exception as e:
                print(f"Error al cerrar la conexión con la base de datos: {e}")

    app.get_db_connection = get_db_connection

    # Registrar blueprints
    with app.app_context():
        from app.routes.main import main_routes
        from app.routes.repos import repos_routes
        from app.routes.usuarios import usuarios_routes
        from app.routes.rutas_gitea import gitea_routes

        app.register_blueprint(gitea_routes)
        app.register_blueprint(main_routes)
        app.register_blueprint(repos_routes)
        app.register_blueprint(usuarios_routes)
        


    return app
