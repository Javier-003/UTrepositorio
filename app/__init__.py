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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGCeXL9uS3S7yaoQS4-cdrreBC8_j9LaRKP5ZgeCkKSB-hI_RoySBH6Iny_Xs95Tw8i31AV1iWxNHtv47OrE4RRtmQ4QadIRCiLWEHNOO-CR1iz__-Ct53JcCDATVg3kS4Kl00ds9KKS8LuOna4sh6DZHlH5jpzd2KPum2HeG8cHbdTKeuZ6vAMTebF9ribLRMAQVoF_Q-IkgME1X0_vPrS6Ad5vA7VItSU1xJ2SBe7gf5-5oMEnRcoFSWi2BZPiVW2PDPMGqGrSfqoaQAQqurKfrEMmI1ai6be690Xquds1sn3iiqyd2scDsCvpSRsHi5z0kMg4OVNVhKyG_zjOvKXlGwZfoBHUF2fLo0V02Qp0ZIiCFk0rLyEn3-DWrZXAVdaig7SsnmUlXqRtw2JmIbAsft4mY3T_IK39LzJKZHt0AGgJLtvUAb1tqMJyiZSB9iMZFkppfXkXEFoyUtjxKK3gC6jq0ESxEGVdOI5hThQgIAcKXeLBT2lD6BhfVm6pmvNIYxFCREICgrReWTXMKtuRI43m7kkpK3r4R_uuvf2ZTtx6m9fhJ5osm_noILrrRuZtGkmT0pGBy35yZDqRYSFV1IWxdnStw7Xbq6zxXNwQVXNNcUB8o_pLTFBWxOr9Cmcl-VqBo4MaHqtKjU_ZGrerbPySFkkePEA7Ch4AiQtkNjF-DYGqhjyTQFviDVJDhaet3OT7Cn8mz6A545PmDohBZznhoXPOWRZ21-63RObqyxkh1ditbjKFF9L-dAoTB9zToROcpQ9E7IUgVo_1247Ohxnr9yJRviHRhLfvrjuv8MA8kdkdf-5dKOobosTp14XBP_F5SXFLStWRJb6DFz2hmgy4zSVZ1ybVzHJal8SQyl4bf3gTni-rZZc5--HJPh26LVogQSa6UsknenM9j2gmKveAJRRVGqM2RWyal1LQVk_b9zN_RGtEW-gD_iNb_DzD4jskekaqL7A4ts4zCR7AzKXRa1czhIF3g8wHRe5XvCrx2gUSLm4sQ7I-4AXCehKNYVF03MnLe-53_r3hILCjGlhx0xcdJCuR4Y8LzF8m-nmN4wVBKU7sWby6FwHRFD3dKNQul_D4jfhKgnhmaTfaton7o-3dH4RBQpPatEtQJHxbaWQt_GdcM09tSWbiCbB85eetpA2bE7IudtitVwpM0c3QkEunRVJPslOW-N5teTO47fbv1KuHAF_ne3xc1RPCmj0_imrpmoQrJkSqz1nnJDCvdxGThZDB8xlGUo47p9PzgnQUMNSzzIxSXVQor1AM7tktnmO_Nzs5xkIWAy8RV59Pf6H9bS8VIrEcCfNRsISDPKweAsX8tmm5d9jCm3TKgP5Bl5Xu2Cnn2PuCAFQwEFH9ye0bqGHcFrTHZeQATaYI72g9AH1UHMKh_zHZuOmwtcJ4R-TrPeIH4JgJZGkcGod4MmLGyn1vlNCQQmL6nDtxP7Ub79BCUqW3kLADaBs"

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
