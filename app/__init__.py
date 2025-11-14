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
        

    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGHNiPsQ-gXQLj9jjjOdF-sTYTg-kveLhwYk4X3gZyk6hMCbBUk-NhQohw3khAsUlyE4JU5abO-oHYyXJjpxprTVrlMgifaxy2X6kEdzuDPRtrqjIOm6bSPzkOrPSQ5-VV_aAbBIMOi2liQ-4ovFzuR8wSron2cSsc-ajSwcnB-1htgkQi3MBnjDYN0X-47-I_XCPBWbZF5i-wwDFlgQZdai_iCXrBht4d_OGfROCxLY6vrUDxnSevipBmGln-zn_pKZA6F8Cs-pxzRteGRH1fxqXeqtCoG6-l1_YaMuIKtzNWr7KbNANOnK7QlfACY-99N-_D8IUzu5xzdi18yu_dIk1qF4UlNwnEhk9I1CDE8sRR46PEznMu6D0CC33g4_DogcwdXNZKyoEnfaqAGwzP-l9sBAt46QRn9a10-dxZtTgTNpVWWm69VRuHMwN_McXMM-fD-zmuIZKFZi9ylh_fvzMYEwTd_v4pV0VK9UIf2YTdDk95UKn74rcZOz7C3nxTbX4yQk8GmY4IWG9T0zENstsR8kRJLYUQx_au8Ax2vwFeYZLj8l5kVURvwF-LOjz8xZZ98G__oxaVollFij2nUT9z-zr9g2gJMG-CbbTTnoeCT08XF3oJux1XSOUBWFTuvW0Rxrrv2FH77OfUw4gbG7EJOl_a3amSQM9E2jD0mTjtlSOYpB3_227uY7Sgvwdqhe23GpuiAFEfr84yeOJ6wCUnN-9pAV_Lvvn8ALgxj8tb99whrt3gHif2SKngO2TrlOtfM4w0xvI9NSg34wEuxtKjsfh9oxk-ETpQy0sap1xi-FKLjT_GFxUZLFUg8hbyk05RAHsmPbG4Z6YgZoj5Oh9dvzSLpQ89YPd1TcEl4eByF8BEf_SbeEQKWgR0OREEBjWoAuv9Tc66L7NZfyqh8Z5lIfoa_fpkjMf1UZmINTu5xb7CwCeMMIHGuG294gd-dD5AOBDPCV2sy1wcR57CAcOcpWuZPAY37ZDydL74WCqzvNGErKE3IW6CmlIHuOnkI1yZplg2i8mFfyuZa4jjWYMjLyXN0UybKwTlJOtjTbv_PVSIuZOMxDDUA5JmkevtEnlz3xTcPQhD5FxKMtndO0prkci9G1vpm_8IBzH4orAnjlpMIGybbxRxL3yf2Xn9SkoL_gzptyzeEWK3BEBaQMnveS_W671ZQjlr6ZBvQ0nqkOWdJ3JNBt-ntR4ujF79cyu2HHHKg_0g7aw3fJPVFupZMdr8wLVzmjGX9lW09VM6HSWlW3goKqn_sB8N4fnA1W5Sxj_3jbIHD8AsqBU6Wus-RSA9mrZKChpJBC9cDAMPEHxM0CTLbUHOth_W41yTABcthriCMAxl26gkfA0SzHPq6lLAt9H_boWIvWCaiHAArKuUyc0TQ0W22Gne4iZhd3bpDk5-xfqq9Xik4rpbpiINuBX_wdDyX7rSrphKTYqw1VuWfoZOKJGD-urZu42bU"
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
