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
        
    app.config["DROPBOX_ACCESS_TOKEN"] = "sl.u.AGAcJfiOzTWHPw1wUUUFFfGdVh2M66XSLr-FWKIGJoJQI42Z8lHqjpsWh407pdZMUw9Fj18qGzXZHYHQCVcb22ySbE5gxgvQE0uSavjkwkedqpNEhP1RLE1xsBnjis4zxORN_NQbg4Ygh6QrEgjUIH6AG3b0aGtOHvABHMw3HMxRSMA3IbpMI4_489tqs4brhEQq48iX9XrwbgKl3bmh0IDuBMq1ZNQg2cVpdPUQYix8L4e-5Dh2XnSS-CiygjnNA4KP8UHvA6k4co9G7PUio2DrhYwTznm6VpuayeRUCMQ8Tj6VHrkAwQSUcAq6oUoDtfXS6mEFeeClE84qfeHU0M1YgWyu-2iuDEe3claC8t-wDrN8LCTZVDRvCi5SfK0nC3FFPKPHaIjqmvLKn0EbRGsFlvlF8oBTXjXofK-4tYUTrNrNjIW1JbdNcSlvah65OdGNYA7mAs8Vx670Emv5TvJSKG5GqH7dlH2K42XbioB4wTmwOWLyi8WaHIe73e3ynDd9F9LMp2RZW2KtkziVztnfj2vEYfjhGWRnX6uZhu8mlUEhy5UT9wdR7pyhRHvZZm72GrG97-KfiAFF5zsUkuMLn_FNTsCLnOf8HJW6Y3g0oasJbWjS7BCBh2gODL7YuNpZKgN8iXia8e_ta4WLHiFOmGmo1gE2BkbgBzNO9otamjkVq0jNAEFeqaTToKyDGf5nrFcjSk_iOg9E40lNYqmqKsXCuyf9ZzJWKLnknTU10nYc9g-4Bgs_4AlDo-FxrbEqACGo8mFcNGbotDbQsOdqygRCAMiDzhUaTuL9ekKwsdrZVzbLeW31-92bNH8uXqaXCSmcKcpBgNEsJ2we4po0L8yNvPoqyfRfv2zUCwsxoAQbU3xmNkOJhHt6Ch0dtGuCWEt9bYn8ZS9WSLj8ygNE3PQkczDZBZ3gUb7Z3aD3yCRvZh7XT_HxzJ8QIevAsxNV84E-hIZwjBkZhV4nsIPL7GbyDL0Nq8qyV8Ofroiv2l_Mc0nhvkZN6K3jYKUKQsktj9RVritLgGYNpuQfF7r7OUhrnG7ckv7hbFRmu8Rd-uTwt6nGq-VFYpUPDXLVQatVXrLqYFlWtnqKNSGlyXAN7xRlADb0kVQfDn2Mw0PPJ-8ML_XUj0Qmd7PFlyCjFn8tm3_KFkQ6De4Hdl7zmWUq6cLK34w1wEJnNgM3frOaDS7JSLvflV2OqRSGiMxtQG6MfmH3PlkHKwNLrRVX_WqFm3QmdxG0QP7OV4w2ps5JOH_TMiV2zJYidnHcEmH5A-OAySWwVT0sBL84QboWnzQ2GBt7YXZqDtWzrNTjcqzFufL02c659FnuS5neWAUFnsf4kT4fkXs4EPanHTzHHEXqn2aQ9LDqOlw66i1jY1uJv264zA__wql6vFfBezQ6GmvEa2RYec1UcHFzrfVvEyUGvLN9dWU2BdkXqE-e1-jc5uthS-gt5zI9JuNJ3iR0d24"
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
