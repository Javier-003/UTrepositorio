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
        

    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGGrfctdQvoOnitGuXkOVgsBak84qyrA8dmeMdMLc1iDSmhQNdaNe_vp9QbWzDa3XHCB5UfZgqN_ZcNAnD8aqm0bl9w8Q_Wg2l-i1aLz4Aq3CIU6mc6ZS4RoA8_m-UwYLTnyxwyvzLTRTfnHodfF0feqEOkdDfohIDqDZi7B98X2RiVh23wjXMWRQcISBCltu-Nvk4m4RISKSDfiApsIOijCT4bSJu345Ki1ii6B1otTpneXMoN1iVd77blmWOd0WLaZ1CThr8zs6-uGEkIvi1tKVk2ZOYdYD9I0Vd4xlvbjI5Y--bBzftCVPnkSa8Tg5zfX3qnSM2lIayKxWvcnB1nFG4S9-irF6ZOYxANR5H0UevSZheA0-EMAS9jvQlmCKGXJXu7JuAgwNf3HGj6f3S_5uwLtZWVcbbsE7XMJcMqBgelLCnAPo3cQNa-xfDi7aROSMYA1qAqfkh3-7KGacLRSOlQSoEI1xehOuBhu1i0TYGmpcwGLGQ8Rr5NWcYx_IWB33Ogfk6edmpbrx3csiwk6ZpMK73mbSaiApEY-G4YwvKZIMKJobAq5GipXEGCzAgvrxx_V6_0jqbP_lbhD8qG9BpUsjzqcbL-0reCrIP4xCLIFqKfLe3CMeKrBPWHJ4HqA1znxVdkjvMwPEUnKrrW2fZsQfnoyD9jvd6zUYxlzvPXYTf-2WuLobLZ3ywtQWjbwA0oaD6aokyPTtLgHukRPaFnJp5W_ByJWiHQsnkgQRQXUsrn74RI-vFnCuABFxjGb23IjWpkzNd6EsXI9RAcOtMlKxskDpEUShYh1miLAMr5KSdb70kq9GuaNb1w4b-4CoEeTTOwYdJK3MOWI99ZFWw2DbxpKKreUR1upuIJuDVHMdyBbjsyHHBXSkcznqltSt-s5ZL5v9fKykqB_37L5cwO-SoTJcE74MjKubYiHHbD1S6NJjBc2gLjb96eueN8_cGuaP0I_1zf3FAMQjIuVsDZWAOltsdspV3AEn0MFX1hLOX6J9UMsPsg88uZgHV6HWs2MxyXt0iP0-VlsAcEdJJzZfzJrmBWE9iDPkH56_SooO37ocmIDj-BsTwdPOk5rW2Yv3O_myzZgiT0oErV3DvE5CQouacW-JCPnTYX-SCc4zsC1gblwNEVlWx9_CUibEl3M1VGo6sbYx3E-N9M4JfclMD7zQZAb7O5Xcnz4Z-703SnHvkvA3Ym9H-4q4t45owqmDnarcnhq9DGZbPxyhluGylR0FrthIDdSFvt37oEnKZf1y8JjbZyaCvJBxgFKR23g6evkqlbgQfFPGN1hWt3EM2ksbt1O0CxaO-EYEGAyBE0f8D7NP07FaPIeKsWiW5v5Zz-5T0BM1N0Cz1-0kBI4F95GKj0b00CNrJ7Ln4aO8scMuhuVRr6QcGFPb_BM4kw_9d3lGInBXf7J3sKSSwuaQbnsHfcwONSh5W7vF0SCqsy33Quyq6Jer9K8uw0"
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
        from app.routes.admin import admin_routes
        
        app.register_blueprint(admin_routes)
        app.register_blueprint(gitea_routes)
        app.register_blueprint(main_routes)
        app.register_blueprint(repos_routes)
        app.register_blueprint(usuarios_routes)
        


    return app
