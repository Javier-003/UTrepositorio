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
        

    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGGGORpMam-3R_Z6JIR-azov0yKAK0JTQZplDJPzG1BT9xW_ODMrbMYbqg6n6viR2q-xZWIsq5Xfiswxismt0sMf3zK8a7iTWQFRYNXoAcgULGtYXKjNC1BflWwUBiTCnqom-TizaGBBV1VENeoViosIq_J1tWS4_LIqRhMPTz86MMforcE7lL1JKzuPoGbzWhc7PJ3Mcb_53_GsG4DrWXPVX_S8uwCD1z8GEH62oUrVkneiZSXg_ViFT0siqpvCIis85BXx9PE4cl4QhfDC9fSNrJA9DcAQHor1-PTiMeIiAgE6lXfUmXyDgrDxRNnKrPOmWKVZA_ENLPeWxMrmEo7f8WD6nIgXgmbRMCXnK46j9RKtXnlRlmENK_VPsM6e9yj-uFVNaoY6tNsK6uXK3IBVg2p5U9yY8Lq5Zx7qt5kwKZLxsrviJuLeJ3qPDy4AdWmoJ1QxrbDmud3m5b69wYAIx8nFUf4gMTKLoNMSH2RJ4yunaPyFwxS0EKRaqjln_RpJwfKI6CHk_i_SBtRJBKeXvlmJ6244or8jB5GvfDbD5HNTQnaJvezIb_4GRe5kxFIzKzfRZUOci2UbuL2xkWzyPRBLiMNbNkyKFsLLNsDzFbz6B-Gb7JF49EfGA-AQfRolzl1pwgle1JJ4S9DMkPNgDY2DCQlzTkK04B_QhEYhVGi3go4teTzBGW6i5kR5Xw6Q3O5b0KmoAt4aXaloF9NcoRPABm7Q3jKCve-bC-onE-4C0CYueGmTkX6j4npd0NqJ82wHyeByWc-53sOPJHcg-U68oxuMA-jtM7tg0dKzNm1aQ7NjALDafsjADA1pdVIl-rSKBbYY335ZgICnl-h-yqbAvISOzEcvzIiar7RatsITid5s4C-U986JgS5LfjJCnJefgY3DDTnBUCsGMTZXU6hAZBoZNyVJy_H6jLIlpj9H2fkkNdqjIWnc506RujODY-sdx6IyxeNIRIJlVqR1L5Zno70bhe6wHHvdg83qfXrD38JAXuu0E426abIbeX0zOq4RRq-26gpPaiVaNvPZhWO2IeduS0g0__tiWMfpU0IGMQ6wINdsu2krxUNPQvMhksVvUh0xfYeJCn2FTMwavUyGLiOoLfbhGSWvNZi1MjW2MhZBTwwVdmnQaPyYZZmkE4mRKmy62fiu4GFnJL9R61u6AkB-GZ6UVvjmSAldGbhzmkJxNLQwHzoBz5ne90gG2A2pmVqxJ8B78ndzAyFuSmnGNvdiXv9J_sSEjVXUvfsAnivjKqwnNzNO3uZZlsl2Q2lHtFoSuF2B9VXLJQdBCp7wZS4LcBe0x8K9_eM9TD-QuMtVcyroPliKzr6rLRtcdFWyeHWqtn4dibHEXQBH-gzXLxu-KxTv_pNmrtAhbAgkz-JyUZ4X399zr8w6_KdXKLNP16XSbaen2YonodEaBvGgDKD9eiHdasnlVEJ6O_WJeYhClHM_M27zkMvPFy4"
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
