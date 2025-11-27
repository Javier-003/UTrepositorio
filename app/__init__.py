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
        

    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGLH6jFyTIa8vA0xGTGH_WQC0avwbb34tsf2SHjMP2ifEVzPS3k_iwP1V2rWl9U-kK1y4tJwx5ROIYvt9xpFBcK3x3Pv22h5mrP934DkN8xJfMLDrPmdBsaMFHvyA4xbidSQHfFKmbLEvaUUKfpejERhrsiq4yAxzPOEKDaPnfAfwbBC5Ec_MXqncGgLnji3E7hYUzb5982UY0mcWncOr48KCDOTVBNQ53xK1WjEyMKgGJDcdtds9aUWv-_R73AXnWb-370tbw6yYHI60uYeYbRZj2RCLO4cIC3DUDyhVSTZ9PRswjMT_sciRgpBql2fMcBCZhCoA83aYfOrw_0PIoKK_oS_ylYAB4RGnASIhH7BpK2Zl7K00nexR_m4MuQb8HkykGAUMwJngTNijWBGVK5en1Gevc9fn_DXA6gWAa2QNruRQ9cCKU19lwHwFF104DBycKMAD-x2YfuUsmv06ZoTHzkCVRqy8LpEODqPKJa1EQxWc0gmtAImApeKdGYKzHHiUi4QUWSS_MYqL-Blp4eDixZLXk47kD0bf5nQErVtR2vD03xxyJ1XGP-eMbsskl3TeigUq2YKaUe0sVGYbD4Riwb9tAwp3KFQpJWGNnn8C1v9db2wJACeNI8sGvQ2RptMPfHIKmoEK8scXig_lNqewRPnuKT62v9Hu8l1H4GE_w1JHlo8eGHzTJ_FP-bd_P6PV1Il6oZD0Gn2WDG9qNUmNNTuhnRjtQ_StJEpx8nRJlkHfMRHmJiJ4F0xSmYZc6JOT2Lp2g1KZm5NXXZps2UcumRj9BZNf-SKBYUMsEktPNhrPu0rEyPXKGlt2oGdGBFv90qq6KC5vsWgIJaOhXwHEVC6dCOWeyL0QcYlErsVjJeKA6dEJxgEL8gPQjNWAFJED2vC7EoyeHavfkgYISo1ettYF5bnRlwrrXD8_Pt0CcWMsfe876-o1kGo25A6a70epb137aCn8fr9wUmXstfg-BHebPrmVlpdWKsLtJsdftCSQ30kMpLyHMLFZtDD92dJcWJSVQsgnwdof9mXquown9_1D2o8C1LAbvSntj_Bcd3w0PCh6nZ7PkBg4kGxqPr9c6PD5G4-7GLgzAJDhlk6xpr17d7L1l8zbdLdYOrzi6kFbr1ZEax_x0BNABOyeCYlgI28_1H3Tny4YyXz2ot3rUwK64Rt8nJZspSTjsC27no4BepT_ZF9ig_tpSksMVTjCdJARs4v-WpwEwh_H4ltC1WqBwBuAq2pYmMH53PMKEQmJZCSdgxiknU5D4ZCJsBKplTlRCTumFv3Kl-IoSsOZlALFkb79c6WayEOrEiHTTib-Q3Z0hta121YS93OXnZDfc2_FyKDGFIpZcApCBI8WDwse8-QmLxatG1z76XMs-nfqT-X2vFWz9-8_-iQaMgfvm4f8lfo5XHjHjQxpcoL_LajVqSBndmHMJAbq_ysrCJjn9SJUs6uvJfM6TEu2W0"
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
