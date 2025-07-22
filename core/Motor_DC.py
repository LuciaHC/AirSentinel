from gpiozero import LEDBoard
import RPi.GPIO as GPIO
from rpi_hardware_pwm import HardwarePWM
import time
import config.variables as V


class Motores_DC:
    """Clase que contiene las funcionalidades de los motores traseros del robot
    """
    def __init__(self, frecuencia, ch1, ch2, ch3, ch4, FACTOR_CORRECCION,factory):
        self.frecuencia = frecuencia
        self._velocidad = 10 # Valor con el que empieza por defecto

        self.ch1_dcha = ch3
        self.ch2_dcha = ch4
        self.ch1_izq = ch1
        self.ch2_izq = ch2

        self.leds = LEDBoard(21, 22, 23, 24, 25, 26, 27,pin_factory=factory)
        # Motor DC 1 -- izquierda
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ch1_izq, GPIO.OUT)
        GPIO.setup(self.ch2_izq, GPIO.OUT)
        GPIO.output(self.ch1_izq, GPIO.LOW)
        GPIO.output(self.ch2_izq, GPIO.HIGH)
        # Motor DC 2 -- derecha
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.ch1_dcha, GPIO.OUT)
        GPIO.setup(self.ch2_dcha, GPIO.OUT)
        GPIO.output(self.ch1_dcha, GPIO.LOW)
        GPIO.output(self.ch2_dcha, GPIO.HIGH)

        self._motor1 = HardwarePWM(
            pwm_channel=0, hz=frecuencia * FACTOR_CORRECCION)

        self._motor2 = HardwarePWM(
            pwm_channel=1, hz=frecuencia * FACTOR_CORRECCION)
        self.encender_motor(self.velocidad)

    @property
    def velocidad(self):
        """Función que devuelve la velocidad actual del coche

        Returns:
            int: velocidad
        """        
        return self._velocidad

    @velocidad.setter
    def velocidad(self,velocidad):
        """Función que cambia la velocidad del coche

        Args:
            velocidad (int): nueva velocidad del coche
        """       
        self._velocidad = velocidad
        self.cambiar_velocidad(velocidad,0)
        self.luces_velocidad(velocidad)

    def velocity_to_duty_cicle(self,velocidad: int):
        """Función que transforma la velocidad en duty cicle. Los valores utilizados en esta función han sido interpolados teniendo en cuenta
        los motores, la alimentación y la frecuencia usadas en el coche.

        Args:
            velocidad (int): velocidada a transformar

        Returns:
            int: Duty cicle resultante
        """ 
        if velocidad == 0:
            return 0
        elif velocidad == 10:
            return 70
        else:
            return 90     

    def cambiar_velocidad(self, v, motor):
        """Función que modifica la velocidad de las ruedas

        Args:
            v (int): Nueva velocidad
            motor (int): 0: Ambos motores /1: Motor 1 /2: Motor 2
        """       
        #error = 15 if v==20 else 10  
        dc = self.velocity_to_duty_cicle(v)
        if motor == 0 or motor == 1:
            self._motor1.change_duty_cycle(dc)# + error)
        if motor == 0 or motor == 2:
            self._motor2.change_duty_cycle(dc )

    def encender_motor(self,v):
        """Función que inicia los hilos de los motores

        Args:
            duty_cicle (int): Duty cicle inicial de los motores
        """  
        duty_cicle = self.velocity_to_duty_cicle(v)      
        self._motor1.start(initial_duty_cycle=duty_cicle)
        self._motor2.start(initial_duty_cycle=duty_cicle)
        self.luces_velocidad(v)


    def parar_motor(self):
        """Función de movimiento
        """  
        self.luces_velocidad(0)
        self._motor1.change_duty_cycle(0)
        self._motor2.change_duty_cycle(0)

    def apagar_motor(self):
        """Función que para los hilos de ejecución de los motores. Para volver a usarlos hay que iniciarlos de nuevo (encender_motor)
        """   
        self.luces_velocidad(0)     
        self._motor1.stop()
        self._motor2.stop()

    def girar_derecha(self):
        """Función de movimiento. Gira sobre su propio eje.
        """  
        GPIO.output(self.ch1_izq, GPIO.HIGH)
        GPIO.output(self.ch2_izq, GPIO.LOW)
        
        # Motor derecho (2) hacia adelante
        GPIO.output(self.ch1_dcha, GPIO.LOW)
        GPIO.output(self.ch2_dcha, GPIO.HIGH)

        self.velocidad = 10
        time.sleep(0.6)

        # Restaurar dirección hacia adelante en ambos motores
        GPIO.output(self.ch1_izq, GPIO.LOW)
        GPIO.output(self.ch2_izq, GPIO.HIGH)
        GPIO.output(self.ch1_dcha, GPIO.LOW)
        GPIO.output(self.ch2_dcha, GPIO.HIGH)
        self.cambiar_velocidad(self._velocidad, 0)
        V.shared.MOV = 'quieto'

    def girar_izquierda(self):
        """Función de movimiento manual
        """  
        GPIO.output(self.ch1_dcha, GPIO.HIGH)
        GPIO.output(self.ch2_dcha, GPIO.LOW)
        
        GPIO.output(self.ch1_izq, GPIO.LOW)
        GPIO.output(self.ch2_izq, GPIO.HIGH)

        self.velocidad = 10
        time.sleep(0.6)

        # Restaurar dirección hacia adelante en ambos motores
        GPIO.output(self.ch1_izq, GPIO.LOW)
        GPIO.output(self.ch2_izq, GPIO.HIGH)
        GPIO.output(self.ch1_dcha, GPIO.LOW)
        GPIO.output(self.ch2_dcha, GPIO.HIGH)
        self.velocidad = 0
        V.shared.MOV = 'quieto'

    def paso_adelante(self):
        """Función de movimiento manual
        """  
        self.cambiar_velocidad(10, 0)
        time.sleep(0.5)
        self.cambiar_velocidad(0, 0)
        V.shared.MOV = 'quieto'

    def paso_atras(self):
        """Función de movimiento manual
        """  
        # Cambiar el sentido de giro
        GPIO.output(self.ch1_izq, GPIO.HIGH)
        GPIO.output(self.ch2_izq, GPIO.LOW)
        GPIO.output(self.ch1_dcha, GPIO.HIGH)
        GPIO.output(self.ch2_dcha, GPIO.LOW)
        self.cambiar_velocidad(10, 0)
        time.sleep(0.5)
        self.cambiar_velocidad(0, 0)
        # Restaurar dirección hacia adelante en ambos motores
        GPIO.output(self.ch1_izq, GPIO.LOW)
        GPIO.output(self.ch2_izq, GPIO.HIGH)
        GPIO.output(self.ch1_dcha, GPIO.LOW)
        GPIO.output(self.ch2_dcha, GPIO.HIGH)
        V.shared.MOV = 'quieto'
            

    def luces_velocidad(self,velocidad):
        """Función para mostrar la velocidad actual del robot mediante los diodos led. Sólo hay tres velocidades disponibles.
        """
        if velocidad == 0:
            self.leds.value = (0, 0, 0, 0, 0, 0, 0)
        elif velocidad == 10:
            self.leds.value = (1, 1, 1, 0, 0, 0, 0)
        else:
            self.leds.value = (1, 1, 1, 1, 1, 1, 1)
