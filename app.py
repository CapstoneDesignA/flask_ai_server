from flask import Flask
from flask_restful import Api
from routes.main_routes import MainRoutes
from routes.test_model_routes import TestModelRoutes
from routes.grandfa_model_routes import GrandfaModelRoutes
from routes.pho_model_routes import PhoOngnamModelRoutes
from routes.hello_model_routes import HelloSnackModelRoutes

app = Flask(__name__)
api = Api(app)

# Register routes
api.add_resource(MainRoutes, '/test')
api.add_resource(TestModelRoutes, '/model/test')
api.add_resource(GrandfaModelRoutes, '/model/gf_factory')
api.add_resource(PhoOngnamModelRoutes, '/model/pho_ongnam')
api.add_resource(HelloSnackModelRoutes, '/model/hello_snack')

if __name__ == '__main__':
    app.run(debug=True)
