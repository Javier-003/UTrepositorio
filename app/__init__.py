import dropbox
from flask import Flask, g
from pymongo import MongoClient
import certifi
from config import Config
from googleapiclient.discovery import build
from google.oauth2 import service_account

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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGA96Ag-YKYByJ4pD8Tx5e39Ru6oh7j1oJmykd71r2aqcqrQelIlmDROGe9cSzIoant09dPCPBhPo8aX3Q2LrjeZsrQ_GmV4VuPCe24J2eidbch9cWrxprOQP9pY9cYHfIfj-jHRjJcTNTDYvKL_JdhMuGT9SBHdtwiUKntUNS6JW1qw4UoG6q_E6f-c0CqLvfOPdvl8F4ZvC65InjkICtEKRZldT0xjoYn-ksMMrYaU-C6NmhlIn4UV0q1Lfo1XdkE-fjz40VrRqYyZQN6c_NXfEtnxlYxArbWqkZ1-LjlPWZvnENPBm17SvXty424yEV9pBkMmVUpjoWMunix4bzNI1NULpVe-qKO5FCC7I8vU35a0n6Gwqeft2kGnQUSxm8CkoOqdp6_d2tvZv3sYHzv10uohVaVgbV6Lau4b3hY-jC2fCIuWbfeKNpldKruU7jAaYa7QbTkvilEkLSNcm2DIVM7TyWI9G6i86QOLNwC7dfhA7ewl8qH20DiGtnJeq-vgp9FUCnGUSA1iDVqj949_N_w-c1Yuv1INfWk9Q1gUVVqxlIMBfA1DDGGDS34_BpNK24KeVXxi4DfpobYOidiMSodXey4CRxD4cCr5NYoF9HUS1FDL6TGsp68dZ8OzfMeObzoD8wX3IlTZYHKimNL8HhAYU3expHdth6OA5V0pLG7YDfrntIuo_7Z63B6EtRBLb-PCZpJsgtCvZ-6drgdDGr-1YUW3eVdgzFVGUfIGTQRGsrXGX30EF-ei4rr5xh7ojypxTlBuo0-m2DmNFSPKCzQeE_W-BKwhXipaqDjoQOvzbaf2n0L9G7eEzRZexuGNZutudqgkzBUcTUNrHJTyMuYmx_NLkRgmj7FcZW7P8y8ZgqvHkJaCKG7nYfFb6rBzyRcS35TaOYE7-19-eOB1S2HawIbVTGtmjm0mTR_NqAkcllRFApgxD9f4jc2bDYCIS9RIXH2BGj4grJjieAYUpH4agK-Hf_OrRu2GxPFZH7ne6jQi57pLcHsfheLFUTKPj47Is1pXZ6z84H9VM_w8EGarPefnBcfgvSx0IaYw2InPt9k_7-hPbrIXuD72199gX9fJZ62wFVWwPo0nNsWsVZQoqjM2FdfFhZmTy9RiS4dHFBdbhkcz7lyN-1VPdT-55YcBvoufQqtoRljnHXeCHNBUWPtTqS0iV_AIPdK5beyt6BnUpUwwjAEh42rHWm8YUYY2_YbREkMcuoRqhEeU3e3dO079rC0L1HEw88BwLWgo_KirblnXN7Tbl7QcFNmDDwoO8oQqPGkVJiXEremATHmSHyaNcIw5rTMEnSLJ2PE_n1KivsItd_9Y7ggU6r4Vl3p_zlO9nqQEHgnG-qyR2druGhLGY91oFbQULsUHwFGiIUTHCMSudriNZoVRHkyzR3bWiPwDwCVaAWL_fhLc-9vOZFiVJOEoK8jusUhXPVGgJAKdD5ExXJfyTQxIFQg"
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
