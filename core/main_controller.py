from gpiozero import TonalBuzzer, Button, LED
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
import config.variables as V
from core.Motor_DC import Motores_DC
from core.Sensores import Sensor_luz, Sensor_distancia, Sensor_humedad
from core.utils import fallo_humedad, enviar_datos_BBDD, deteccion_fallo, arreglo_coche
from gpiozero.pins.pigpio import PiGPIOFactory
import time, datetime
import board
import adafruit_scd4x
from threading import Timer
import socket

def main():
    """Función que contiene el bucle principal del programa
    """   
    # ---------------------------CONEXIÓN INALÁMBRICA 2----------------------------------
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)  # conexión con el ordenador local
    server_socket.bind(('0.0.0.0', 6000))
    server_socket.listen(1)
    conn, address = server_socket.accept()
    print("Conexion desde: " + str(address))
    # Envío de datos al ordenador local
    timer = Timer(20, enviar_datos_BBDD, args=(conn,))
    timer.daemon = True
    timer.start() 

    vel_previa = V.shared.velocidad
    modo_previo = V.shared.MODO

    # ---------------------------------ACTUADORES---------------------------------------
    factory = PiGPIOFactory()
    # Buzzer
    buzzer = TonalBuzzer(16)#,pin_factory=factory)
    # Motores DC
    motores = Motores_DC(V.frecuencia, 4, 5, 6, 12, V.FACTOR_CORRECCION,factory)
    # Pulsador de arreglado
    puls_arreglado = Button(17, pin_factory=factory)
    pulsador_arreglado_o = puls_arreglado.value
    # # Pulsador de apagado de emergencia
    puls_apagado = Button(7, pin_factory=factory)
    puls_apagado_o = puls_apagado.value
    # # LED de emergencia
    led_emergencia = LED(20, pin_factory=factory)
    led_emergencia.off()

    # ----------------------------------SENSORES----------------------------------------
    # Sensor de distancia
    sensor_distancia = Sensor_distancia(1)#,factory)
    # # Sensor de humedad
    sensor_humedad = Sensor_humedad(3)#,factory)
    # # Sensor de luz
    sensor_luz = Sensor_luz(0)#,factory)
    # Sensor CO2, temperatura, humedad
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)
    scd4x.start_periodic_measurement()
    time.sleep(5)
    try:
        while True:   
            if V.shared.MODO == 'automatico':     
                # APAGAR/ ENCENDER EL COCHE
                puls_apagado_previo = puls_apagado_o
                puls_apagado_o = puls_apagado.value
                if puls_apagado_o < puls_apagado_previo:
                    time.sleep(0.05)
                    if puls_apagado.value == 0:
                        if V.shared.ESTADO == 'apagado':
                            V.shared.ESTADO = 'encendido'
                            print('Coche encendido')
                            motores.encender_motor(10)
                        else:
                            V.shared.ESTADO = 'apagado'
                            print('Coche apagado')
                            motores.parar_motor()
                
                # Cambio de manual a automático
                if modo_previo == 'manual':
                    print('Cambio a manejo automático')
                    motores.velocidad = 10
                    modo_previo = V.shared.MODO
                
                # ARREGLAR LOS SENSORES DE HUMEDAD
                pulsador_arreglado_previo = pulsador_arreglado_o
                pulsador_arreglado_o = puls_arreglado.is_pressed
                if pulsador_arreglado_o < pulsador_arreglado_previo and not V.ARREGLADO:
                    arreglo_coche(led_emergencia,buzzer,motores)

                if vel_previa != V.shared.velocidad and V.shared.velocidad == 0:
                    print('Cambio de velocidad a: ', V.shared.velocidad)
                    vel_previa = V.shared.velocidad
                    motores.velocidad = V.shared.velocidad

                if V.shared.ESTADO == 'encendido' and V.ARREGLADO:
                    # Se detecta un cambio de velocidad hecho desde el servidor web
                    if vel_previa != V.shared.velocidad:
                        print('Cambio de velocidad a: ', V.shared.velocidad)
                        vel_previa = V.shared.velocidad
                        motores.velocidad = V.shared.velocidad

                    # Se miden las variables ambientales y se preparan los datos para enviar a MySQL
                    if scd4x.data_ready:
                        humedad = (scd4x.relative_humidity +
                                sensor_humedad.interpolar_humedad())/2
                        dato = (scd4x.CO2, scd4x.temperature, humedad,
                                sensor_luz.interpolar_luz(), datetime.datetime.now())
                        V.shared.datos.append(dato)
                        # Si falla uno de los sensores de humedad se para el coche para arreglarlo
                        if fallo_humedad(scd4x.relative_humidity, sensor_humedad.interpolar_humedad()):
                            deteccion_fallo('Fallo de humedad detectado',buzzer,led_emergencia,motores)
                            humedad = 0
                        # Si se superan los umbrales de seguridad de las variables ambientales se genera una alerta
                        elif humedad >= 75 or (dato[0] - 400) >= 900 or dato[1] >= 60:
                            deteccion_fallo('Se ha superado uno de los umbrales de seguridad',buzzer,led_emergencia,motores)
                            dato = (0,0,0,0,0)
                    
                    # Si se detecta una pared gira (modo automatico)
                    if sensor_distancia.verificar_cercania():
                        print('Obstáculo detectado.')
                        motores.girar_derecha()

            if V.shared.MODO == 'manual':
                motores.cambiar_velocidad(0,0)
                if V.shared.MOV == 'derecha':
                    motores.girar_derecha()
                elif V.shared.MOV == 'izquierda':
                    motores.girar_izquierda()
                    motores.parar_motor()
                elif V.shared.MOV == 'arriba':
                    motores.paso_adelante()
                elif V.shared.MOV == 'abajo':
                    motores.paso_atras()
                if modo_previo == 'automatico':
                    print('Cambio a manejo manual')
                    modo_previo = 'manual'

                

    except KeyboardInterrupt:
        print()
    finally:
        motores.apagar_motor()
        scd4x.stop_periodic_measurement()
        led_emergencia.off()
        GPIO.cleanup()
        conn.close()
