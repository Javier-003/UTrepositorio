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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGAnO9Q7ZdofKBX-aBWXm3OFYtOaNPJ0S6kawX190Q5oc3EVDzDK8jlIITL_jdDy9wow3LVK6wGuTaI7ETke6gj2QFnq6_GhWHS4pdcDx9snves58KxhI0HOPrxnkw0Tb0iZhUgdllbUNjFgHSeNMW6UZPEruiipcU724fUlhYSTYZV9z-hFkyaUvb_Z5pbK-OQmSoslpxSMPtgAiOiQ5N7HOT1UJUwf9-f9QuqxjWuBEZNNtXgDrdQnwgzaPGJFlmXeQOx-rm-uw2dQUtlB7W2WNPfN6LD9UnnVgd7O_DbUZ3HWHc5Isic8-PXd1So3emOaYAvxc5N0BYAV7zd6_q0_CjWSCG9W8GOCzkd_Ec3BgzfEErBihRWCSWvCgcQX6aoGFsk9gzD-LirSnSYHXtxzms-fv08bgiIU8BO2wU637DJP1CuTEL_8GHi0g0UCDX0VJtGOHztPYKFz_muYz31-w-g-oT43Suuz6kBjxWhBP-596fsa4JCZXDr-eIJQddp_B7bnRq3DjXP45cJME24bTpdvgBj9bDqqCsVVxMKUsrhbTAUzy7QOaWSUzEIDb2_zStgxawH8dj4iWb8VueTJqLrKQoBYZVgmXxHfU9smB28RPJmLy_Uuz6xHwXo3MfSu6eKO1YkjSZbmGyWi6WDO4coEZzmiSdk7gnMmHo27zBcSk3BHOEk4f9SP5tm3XSaDn3mi-KZtXu2LRz3_-Dbk_clxMBVw_bH-yMAThDUx-hkd4U05G0Gdd4j8wptoY9kZ7M3n5ZSZa6TLsks5LsP36dw-URLyzot0hCRZ8NL6lr7ITyi4thK_CyEPJlhHKS5RZk_T7HYRviLyGOEXD5gCtaWx9b0m21uSBa9waUKf4X49J26ssyuORamSJFtKGF2Cj2ZUcV8KuZ3zlLojOaY5E7gH53lBWrSs8QehfEM59L0EyPCHkjDJzk2XS6_br6-iSiXC7ABcXFECe430XJcY4OWNKZgQClA6K6ksdT87q0kzjmsMfvMdZ6bgJeyIu4j_rmhzdLYKymPJgCX6QB3NwRx-EKlnbCuQuhPnWJqDe7UtgVo0UGxJwhtkM1-98yyGvWY1cXGyY5Oz0J-M1Gir6HwTE8Xo9qvI3k2tWL1EUPuL29do_J4dACDgkGllxdk0DVZ9ypp-c5cMHkzj6yO3PEfs3QIFejF8zjWRaMfzll6a4bKRvKiJls0ZTx3T2sdNfvTBm8-TgBHmF7aQqRgatzDjH8xspm3ZRObkGupmqPBSWDKn6qQ9w672hj2pC1MTKzu2pSVLllAh2yzX0YfOOu6EdftHnMtAZOKS0xSXFNZ6RSs0oUNMujOEHFGOOU2JRqFFL4C3m_jziOfRDdYiNJ2Hq3oi6fpSTJo2aUUiC024j4iY9JbYDUBoHRQ0-hr9yKR_LhNfpT3e3qobIkvCUtBeDG_5jkxXW-d76vnIRrfv12TpIik80Gsk-Bybakk"
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
