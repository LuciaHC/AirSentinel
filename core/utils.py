from threading import Timer
import config.variables as V

def fallo_humedad(humedad1: int, humedad2: int, diff=50):
    """Función que indica si existe un desajuste grande entre las mediciones de humedad, indicando el fallo de uno de los sensores.

    Args:
        humedad1 (int): humedad del primer sensor
        humedad2 (int): humedad del segundo sensor
        diff (int, optional): tolerancia admitida. Defaults to 50.

    Returns:
        bool: booleano que indica si existe fallo o no
    """
    return abs(humedad1-humedad2) > diff 

def enviar_datos_BBDD(conn):
    """Función que se encarga de enviar los datos al ordenador conectado con la base de datos de MySQL.

    Args:
        conn (socket.conexion): conexión con el cliente
    """
    datos = V.shared.datos
    # Unimos los datos en un string
    mensaje = ''
    for dato in datos:
        for valor in dato:
            if valor != dato[-1]:
                mensaje += str(valor) + ','
            else:
                mensaje += str(valor)
        if dato != datos[-1]:
            mensaje += ';'
    V.shared.datos = []
    # Enviamos los datos al ordenador local
    conn.send(mensaje.encode())

    # Creamos el siguiente hilo
    timer = Timer(20, enviar_datos_BBDD, args=(conn,))
    timer.daemon = True
    timer.start()

def deteccion_fallo(fallo,buzzer,led_emergencia,motores):
    """Función que ejecuta las acciones que ocurren cuando se detecta un fallo

    Args:
        fallo (str): mensaje del fallo
        buzzer (gpiozero.Buzzer): buzzer
        led_emergencia (gpiozero.LED): led
        motores: motores del coche
    """    
    print(fallo)
    V.ARREGLADO = False
    buzzer.play("A4")
    led_emergencia.on()
    motores.parar_motor()

def arreglo_coche(led_emergencia,buzzer,motores):
    """Función que se ejecuta cuando se arregla el coche

    Args:
        buzzer (gpiozero.Buzzer): buzzer
        led_emergencia (gpiozero.LED): led
        motores: motores del coche
    """    
    print('El coche ha sido arreglado')
    V.ARREGLADO = True
    led_emergencia.off()
    buzzer.stop()
    motores.encender_motor(10)
