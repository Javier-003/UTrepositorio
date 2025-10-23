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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGCLwGAuO98He3hyiuiO4Fs3f3tKyWxZ4C6m6RDhO7u7wVQQDDvmTuaOspw87kqFYXgUNsX9f08Maq9Y7jZ3UbkNl6cXTVtjNU3rgw1WIMhuQtM3oiIOu_mhLHnRc2RRwG6R8NjOxrVT2U4uy_vdoOO7EkoClzXSEDTnkQMYL1cnIm5_NUf6mNe8fAhPlmxUiBpWgOcDM-oIdCBNubDFi2Fbm8HPmRqDIJ6TAMES5Kh-4WT7dxUSogF4ezJURz_0uuH3vzINUbOlkwbr991BwGVikAsfHpZ15vLj07gX64g7n0t_-4G3-fLvjwBdS6V1fL3FnPgJCuiVyyDVTodE5pm_wQB7qCpu7q3PHV_2NKBiLapKDImCQTVnl0MUWAZD_FPtTxSWNg2NSetl3-m33dh9hIc8FIiMFhdHwQYSccHfS81h1K7HETP4Cqza25KXbrbHWZ-KFEibg51BjKATed9PnGlnPGU05dZURQ_Xu-kFk3RvsgUHg21SdC21CMne0atlqyvnFB4VqPmD9TkMZnNYT5B8v4Eg-PC9-WC2EDhWJMs3ojgbYsasMxVCT7Dt10fEaZ-JvQECdU0Kobym2gCTUSYJsFZoLW3q3_7nZz0nQOkfeAF4ZHuW7K9toLKFQPPmfIzAfX---pE8k-WPFJndvOgOoefCsPChExlSwaL7tHi-uoE-NK8-dLhwx1kPTBw2whjqoS8vIqGd_LgU0e8_ZnVzy7ailpB2hqmEjO6dUQfbnsbdxXdfqfwozOk62UMaCtHw7MyVXAbTKlDB_KfSJXR-ICOW4vPbkQjc-kSFCX6qaLyYtIm3zs7HsqPA-H4gR5lZh-F5STxMLE63QNYk4K8jCQ6t3l4sL2vjYUq6GEJZrmIwFwrlm8BR-b_h4XdaSWUIBQojXEMzmDwyI_PcJWT90n_3nr_JwR-y2aaFcmjnoa7Zm7XztBq12vaaivtR3Nc37SvFuMbqbFlLrVPQi69fs8wMKSxcNKQMqahzgk_ovIUcpsYDDCn8D1OFaXzePi_BzKr8AmsjCQ1nbDtnLk5IRTcBfttXMbNYOLBeft4L4hmKeA6DFxAlGtZeIT2cJLgenv0BdENn50ZpWkC0wo_Suo1jfgUXjMxjYzlgRPqDBKaR3HTcFhRxhJKvgajFTjS5hONtjhf1x4PcLLCLNLsfEE1iN6iul6lfyjmLyY6PMa1aSkBSBy1HMOGWyPqQ-7G6exdkqfd9kkvPt6M0l6i0jMtSGzXxm-8ilPVvg_yADUzmef7b2Nic0PwfLzB71xjprRSmToXfH80ww8VsTPVzdNWmmdhS11b89oHjoj6flCqR7xnP0cuOiE_z2ok0_ygPgUqspVwMd1f8n1h6Cje8DlS8NDL3lv-T3QKrGGvTRquzlsfqlDQlfMASfGO9bqNSVIXoq9Il8GH7ueN2JBYu1zdnw9sZT90xB-rV6_F2spDGzoeXaEI0fx3jeB8"
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
