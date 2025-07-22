from gpiozero import MCP3008
import board
import adafruit_scd4x


class Sensor_distancia:
    """Clase que contiene las funcionalidades del sensor de infrarrojos de distancia.
    """

    def __init__(self, channel):
        self._sensor = MCP3008(channel=channel)
        self.memoria_distancia_v = []

    @property
    def voltage(self):
        return self._sensor.voltage

    def interpolar_distancia(voltaje: float) -> float:
        """
        Dada la lectura de 'voltaje' en la salida del sensor,
        devuelve la distancia estimada (en cm) mediante interpolación lineal.
        """
        voltajes = [0, 2.3, 2.55, 2, 1.5, 1.25, 1.05, 0.90,
                    0.8, 0.75, 0.6, 0.55, 0.51, 0.5, 0.49, 0.48]
        distancias = [0, 10, 20, 30, 40, 50, 60, 70,
                      80, 90, 100, 110, 120, 130, 140, 150]

        if voltaje >= voltajes[0]:
            return distancias[0]

        elif voltaje <= voltajes[-1]:
            return distancias[-1]

        for i in range(len(voltajes) - 1):
            if voltajes[i] >= voltaje >= voltajes[i+1]:
                dist = distancias[i] + (
                    (distancias[i+1] - distancias[i]) *
                    (voltaje - voltajes[i]) /
                    (voltajes[i+1] - voltajes[i])
                )
                return dist

        return distancias[-1]

    def verificar_cercania(self, umbral=0.15):
        """Función que verifica la cercanía del sensor con posibles obstáculos. Esta función tiene en cuenta la monotonía 
        de la función de ajuste del sensor proporcionada en las especificaciones.

        Args:
            umbral (float, optional): umbral de detección. Defaults to 0.10.

        Returns:
            bool: booleano que representa si el robot debe parar o no 
        """
        voltios = self.voltage

        # self.memoria_distancia_v.append(voltios)
        # if len(self.memoria_distancia_v) > 10:
        #     self.memoria_distancia_v.pop(0)   # Eliminamos el dato más antiguo

        # if len(self.memoria_distancia_v) < 3:
        #     return False  # No hay suficientes datos para evaluar el patrón

        # # Extraemos las últimas tres lecturas
        # v_anterior = self.memoria_distancia_v[-3]
        # v_penultimo = self.memoria_distancia_v[-2]
        # v_ultimo = self.memoria_distancia_v[-1]

        # # Verificamos que hubo un aumento y luego disminuye
        # if (v_penultimo < v_anterior) and ((v_penultimo - v_ultimo) >= umbral):
        if voltios >= 2:
            return True
        return False


class Sensor_humedad:
    """Clase que contiene las funcionalidades del sensor humedad.
    """

    def __init__(self, channel):
        self._sensor = MCP3008(channel=channel)

    @property
    def voltage(self):
        return self._sensor.voltage

    def interpolar_humedad(self) -> float:
        """
        Aproxima el % de humedad relativa (RH) a partir del voltaje
        de salida del sensor, usando interpolación lineal entre puntos.
        """

        voltajes = [0.50, 0.6, 0.70, 0.80, 1.00,
                    1.20, 1.40, 1.60, 1.80, 2.00, 2.20]
        humedades = [0,   10,   20,   30,   40,
                     50,   60,   70,   80,   90,  100]

        voltaje = self._sensor.voltage
        if voltaje <= voltajes[0]:
            return humedades[0]

        if voltaje >= voltajes[-1]:
            return humedades[-1]

        for i in range(len(voltajes) - 1):
            v1 = voltajes[i]
            v2 = voltajes[i+1]
            if v1 <= voltaje <= v2:
                # Interpolación lineal
                h1 = humedades[i]
                h2 = humedades[i+1]
                # pendiente
                pendiente = (h2 - h1) / (v2 - v1)
                # valor interpolado
                humedad_calculada = h1 + pendiente * (voltaje - v1)
                return humedad_calculada
        return humedades[-1]


class Sensor_luz:
    """Clase que contiene las funcionalidades del sensor de luz
    """

    def __init__(self, channel):
        self._sensor = MCP3008(channel=channel)

    @property
    def voltage(self):
        return self._sensor.voltage

    def interpolar_luz(self) -> float:
        """ Función que interpola la intensidad luminosa en función de los voltios que recibe el sensor.

        Args:
            voltios (float): Voltios que recibe el sensor.

        Returns:
            float: Intensidad luminosa interpolada.
        """
        voltios = self.voltage
        Vo = [0.5, 0.51, 0.53, 0.57, 0.58, 0.6, 0.62, 0.67,
              0.7, 0.75, 0.78, 1.16, 1.8, 2.48, 2.9, 3.5]
        L = [0, 40, 60, 80, 100, 150, 200, 250, 300,
             350, 400, 500, 600, 800, 1000, 1200]
        indice = 0
        for i in range(len(Vo)):
            if voltios < Vo[i]:
                indice = i-1
                break
        l = ((L[indice+1] - L[indice])/(Vo[indice+1] - Vo[indice])) * \
            (voltios - Vo[indice]) + L[indice]

        return l

