from multiprocessing import Manager

manager = Manager()
shared = manager.Namespace()

# Velocidad del robot
V_MAX = 40
V_MIN = 0
shared.velocidad = 10

ARREGLADO = True
shared.MODO = 'manual'
shared.ESTADO = 'encendido'
shared.MOV = 'quieto'

FACTOR_CORRECCION = 0.933
frecuencia = 20000

shared.datos = manager.list()
