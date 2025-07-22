import socket
import pymysql
import configparser

config = configparser.ConfigParser()
config.read('config/configuracion.ini')


def crear_base(cursor):
    """Función que crea la base de datos sólo si no existe ya para no eliminar los datos.

    Args:
        cursor (pymysql.cursor.Cursor): Cursor
    """
    print('Creando la base de datos y las tablas')
    mysql_database_name = 'SSEE'
    # Creamos la base de datos
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database_name};")
    cursor.execute(f"USE {mysql_database_name};")

    # Tabla
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datos (
            time DATETIME NOT NULL,
            humedad FLOAT(10) NOT NULL,
            temperatura FLOAT(10) DEFAULT NULL,
            luz FLOAT (10) DEFAULT NULL,
            co2 FLOAT(10) DEFAULT NULL
        )
    """)
    print('Base de datos creada')


def actualizar_base(cursor, mensaje):
    """Función que se encarga de enviar los nuevos datos a la base de datos.

    Args:
        cursor (pymysql.cursor.Cursor): Cursor
        mensaje (str): String con el mensaje enviado desde la raspberry pi
    """
    print('Introduciendo datos en la base de datos')

    mensaje_list = mensaje.rstrip(')').lstrip(')').split(';')
    sql = """
        INSERT INTO datos (time, humedad, temperatura,luz, co2)
        VALUES(%s, %s, %s, %s, %s)
      """

    carga = []
    for datos in mensaje_list:
        dato = datos.split(',')
        carga.append((
            dato[4],
            float(dato[2]),
            float(dato[1]),
            float(dato[3]),
            int(dato[0])
        ))
    cursor.executemany(sql, carga)
    print('Batch de datos enviado a MySQL')


if __name__ == '__main__':
    # Establecemos la conexión con la base de datos
    conexion = pymysql.connect(
        host='127.0.1.1',
        user='SSEE',
        password='123',
    )

    # Establecemos la conexión con el servidor de la RaspBerry Pi
    host = '172.20.10.11'  # ip del servidor
    port = 7000
    client_socket = socket.socket()

    try:
        cursor = conexion.cursor()
        crear_base(cursor)
        client_socket.connect((host, port))
        while True:
            data = client_socket.recv(1024).decode()
            if data == '0':
                break
            actualizar_base(cursor, data)  # Enviamos los datos a MySQL
            conexion.commit()
    except Exception as error:
        # Cerramos las conexiones
        print(error)
        cursor.close()
        conexion.close()
        client_socket.close()
