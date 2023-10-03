import json
import routes.routes as routes

from flask import Flask
from flask_restful import Api
from database.db import initialize_db

# Initialize Flask app
app = Flask(__name__)

# Configure database on localhost
app.config['MONGODB_SETTINGS'] = {
    'host': 'db',
    'db':'maliciel_db',
    'username':'maliciel_user',
    'password':'maliciel_password',
    'authentication_source':'admin'
}

# Initialize the database
initialize_db(app)

# Initialize the API
api = Api(app)

# Define the routes for each of the resources
api.add_resource(routes.Tasks, '/tasks', endpoint='tasks')
api.add_resource(routes.Results, '/results')
api.add_resource(routes.History, '/history')

# Start the Flask app
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'))
