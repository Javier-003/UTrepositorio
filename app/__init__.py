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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGB_WvBetwsIdWAX4UVt8HZ-oGjiGcL7ukR-CkiRyZwk5fHUbM_drN0civC1opjAZlVo-fKkHmDffw26bU_j4TaHFp9P9JhlEqc767KuE4QjStgTOgf9tABEQp4AZHI5ZZUmH4LRslQX5l4hojiZ6q8Q2cjzZEN7CnKvcVyspghw5N_SzhJqS02CMiukWRRBsgwYftWSn01yquz6rU6jW-X0q_Fmvh3QNlQTjm3PST_AhFjbnvt1yRn9UQuzO7j4sTVaR8CfiSR2mrfGfMLsN0Ao8xgrf07kgl7cGgdgw6CaR14FCBzRSpRLunjUnGq2A_mzCpPZ_gxsciKGcl08ZolczhQULONTPVib2wabl5llrvu_iXvwJBOtJkUNGVbfS4lDGsTbX9LyAIf7aiBANaeKq0USFCF2POYLefmjQaW0wFbL_sQ1VxODvP125zKgcycQ7UcvLpgqmnX-PN3vGxUUmME91DYmLuRWl-u8yGsnb2JJ4qCC0nPGrX-b35PgrSszRIWxQC1FvsjYX3G-2oyZXg4rZ1JmdZa6ocoMER4Ka_mmgcRvdZQWRRWLjhb9AYnHT5PmyiLSh-qn47kVEJA6sWJnH-hYtBg-2lLy5qvEbCgYOdll43sa84cFoyupD6174aMIeTe48V0CpZMr_vyRAdbDMI296mcED91wd4WChJX2xmHV7TMkts_zj-ohTIGj0AqT2R_cQLQ4hsK-6nqYdizf16F7_J3GXtII-xwbym7xV325a-3Dca6B8A7Wgfvi3_Hs73AhKk-Z3-aLzeACdMB-QDsfozvlTjTyhTnCUogrutpv2PqddQMH4k-VW7d9L-un2IZ-9QWaZ4QYPRdietwK1yLkLaagko9Z46KiGyH1ZKPI_AJARILFh-wx1Q9FOo-m4jpv83oYpHIv1hQecBzGZv9fLfwL567Nz4Z1bsdaoYRzDwma-hxW_FU0swrxRdB3wr-mFDKZ-yc4zlDIUvDysR7GBQfoTRInPswsIOJV3I-6TSgOPUt-96sPQFHPgmicOIgRNHZv_kxsWp0kl7eoSvMI0bw-zQlmKNO-CyBhhvCWveHPlgiuRrbNlYoOs-dfoGhku7FC8_D-1KYPBaYfzhhz5rrSbP-DjKV1FHgdkFRpzWOAOSIT5bUcpPnxtaIIvfTz7BfVghqp3urStD5InhRnNCAkJgCQX6PJYzzAO1YN3U71Wa9dFxpFoeXvtq0skmOm6dwLRZ18IWx7vFqoMH_u9wdwWmNoVRTSIwXknycmk41H-QBGZPm9URWPeDMZI3Gp6m0LfXHel4UH-q2BttZ5lvxNQDHE-ekDQy_uKsPd0c8xNW0n0---1B_z4npmKI9IwJm1FKkpEisEWYZbuFVDmA5Z_cUY6q82PN4zryT8wiFZBtPyOvsCfieodi8CM0aNQmmsG5TKRycxW3Hczwrt2Wi3umG3A23i1JzgPM34FjASFXAhavwG3D4"
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
