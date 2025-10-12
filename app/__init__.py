import dropbox
from flask import Flask, g
from pymongo import MongoClient
import certifi
from config import Config
#from googleapiclient.discovery import build
#from google.oauth2 import service_account

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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGBEh3yCc4QRVGoMk2X-vy3TpsKs9o-3bq0jNyTsC0ReupFuDUahN7dxN-PYAH7t8viDFBbZYX2n-HBPiInLQnxafr_GHJpp9KfFHzElpNheXrpCw8AxlJgbfXnrkp0IHIiR3wkGTf5cZxI_4Hxr7i9KUaU60IV0U4oFodJiGqefXLGh0R0O_tJFhAk29x9SqqwJ19QptwPITWmCeFAKQvKyCMdRwee5A4iUG9TCECe3JN0KnN0zfOJZlLtNDonqeleNJ_8NiSrypO4IcD_vTbloX-5cUxUsoNSA5JTfOAB6NPHNPXFxWK9ryCaajpKRy0OihDCndf1NHDhUlcGKjntoQTJ3N2s4KziOVhM2FFm6zKbfdIGuCEaer7O41JJuJv2WH0XhTBo78z1Ur76CD-W72ow_XaST7eO1NdW819TIiCMDr4YCmAiywxLQViKucdjetTkZtzEFcsJkIXl_2jCYu6BzPwpaeTmOCLZ4OrFZy1vNB_rhn5BURE58zr_eSJ_JNgcc8ejwD_gIjJK6o8W-TtJtxtQx7PgWHyf5LPjz-uCYyZvGDOHSZq3vEll8Ey3Tzq5E3L8cvVizw0o7LoejLMzon7Uj5_XWsUaK36WdvvJtupFiJveN8ECrfJV1faSeZmeETDVGv0N68BkitSJMd2FkoRLi7kQdVZ9cHej5uJYnWcV4TAchvhv2wonuny_vWvkMfZEyfrHHsNPjCnu4E80avTz5-MOEzd0yUgkecUJd74wwAJxzQDNHNT4xaGoqNrmZNcyGtMmlrnc40UjrhtZVitCqavVAiqFlqMj-ky4EcWPvn_ajkIQ-wBGNk-vcAwaZD7dWVE2zd_hfsEKAZZDc0SYIuAL4z2MDxZIfSWsHy_0xDqcWMEE6ues4IOdr_kXJTV9qrZ3vNFhi7mpf_EMI2Fbj9HssnA8d-aR3TuIuA_jm-Li1RaZean_My0y1uFZ_etE9pgJYBmS9WPkDkti_0STKZEMlKpcgs82GsAJYQoSDAKQvy8gW2zZrw3BDP27XvP_6rXNBqnmSS3TfejnNxPRs4ssFc00v9RDoCLc4NAvy9N_W3_Vmc7kgA6x4ZyPze4XJynC2B5IqP5qTskiCDVLE90YqDfs1gdeyyxQD6irWH8Fyv8Se1dMOXYOXxyBzmu6RJhxbFyQR0NYJIYOSxI10W3fh1KLHeUHkZx6Hh0YI7ChDS_6WgjITk0qFKWDZbEZiCiZe8ywHWbIVd5TziPXk_Y85ur9bmxTS2nQFd-TpTueozu2pGXyX8dSBNbYkn8ZXBtfGIh7qKIKwmCadEgJg8GiHvH093tJ6_0QOylUSHndR6IGwo8861CtBi25_IdJARYJynCu1r2AysTYKQv5YkpWcvpMbCW_OCbV6L-tydXI4TKr64iRvG1QYb5JWFc2pnVB_iWPaHbjTNDCqLXY1oWx5h-O1xVpf6zNqmSUcc40zyC4AATYbjb4"
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


        app.register_blueprint(main_routes)
        app.register_blueprint(repos_routes)
        app.register_blueprint(usuarios_routes)
        


    return app
