from multiprocessing import Process
from core.main_controller import main
from app import socketio, app
import os


# Ejecutable del programa
if __name__ == "__main__":
    try:
        os.system('sudo systemctl start pigpiod')
        # Funcionalidades del robot
        robot_thread = Process(target=main)
        robot_thread.daemon = True
        robot_thread.start()
        # Conexión con el servidor de la web
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except Exception as error:
        print(error)
        robot_thread.join()