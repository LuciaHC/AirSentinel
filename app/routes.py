from flask import render_template
from app import app, socketio
from flask_socketio import emit
import config.variables as V


@app.route('/')
def index():
    """Página principal
    """    
    return render_template('main.html')

@socketio.on('change_velocity')
def change_velocity(vel):
    """Función asociada al botón del servidor de cambiar velocidad

    Args:
        vel (str): nueva velocidad
    """    
    try:
        V.shared.velocidad = int(vel)
        if int(vel) != 0 and V.shared.ESTADO == 'apagado':
            V.shared.ESTADO = 'encendido' 
        emit('velocity_response', {
             'status': 'success', 'message': f'Velocidad establecida en {V.shared.velocidad } m/s', 'current_speed': V.shared.velocidad })
    except Exception as e:
        emit('velocity_response', {
             'status': 'error', 'message': f'Error: {str(e)}'})

@socketio.on('on_off')
def on_off(state):
    """Función asociada al botón del servidor de encender/ apagar

    Args:
        state (str): on/ off
    """    
    try:
        if state == 'on':
            V.shared.velocidad  = 10
            V.shared.ESTADO = 'encendido' 
            message = 'Robot en estado ON (velocidad 20 m/s)'
        elif state == 'off':
            V.shared.velocidad  = 0
            V.shared.ESTADO = 'apagado'
            message = 'Robot en estado OFF (velocidad 0 m/s)'
        emit('on_off_response', {'status': 'success',
             'message': message, 'current_speed': V.shared.velocidad })
    except Exception as e:
        emit('on_off_response', {'status': 'error',
             'message': f'Error: {str(e)}'})

@socketio.on('mode')
def mode(state):
    """Función asociada al botón del servidor de cambiar el modo

    Args:
        state (str): manual/ automatico
    """
    try:
        if state == 'manual':
            V.shared.MODO = 'manual'
            message = 'Robot en estado manual'
        elif state == 'automatic':
            V.shared.MODO = 'automatico'
            message = 'Robot en estado automático'
        emit('mode_response', {'status': 'success', 'message': message})
    except Exception as e:
        emit('mode_response', {'status': 'error',
             'message': f'Error: {str(e)}'})

@socketio.on('direction')
def direction(state):
    """Función asociada al botón del servidor de cambiar de dirección

    Args:
        state (str): ARRIBA/ ABAJO/ IZQUIERDA/ DERECHA
    """    
    try:
        # Solo se mueve el coche si está en modo manual
        if V.shared.MODO =='manual':
            message = f'Cambio de dirección: {state.lower()}'
            V.shared.MOV = state.lower()
            emit('direction_response', {'status': 'success', 'message': message})
    except Exception as e:
        emit('direction_response', {
             'status': 'error', 'message': f'Error: {str(e)}'})