from flask import Flask
from flask_socketio import SocketIO

# Inicializamos el servidor de la web
app = Flask(__name__)
socketio = SocketIO(app)

from app import routes 