from flask import Flask
from flask_restful import Api
from routes.main_routes import MainRoutes
from routes.model_routes import ModelRoutes

app = Flask(__name__)
api = Api(app)

# Register routes
api.add_resource(MainRoutes, '/test')
api.add_resource(ModelRoutes, '/test/model')

if __name__ == '__main__':
    app.run(debug=True)
