
import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Cliente_address = ('localhost', 10000)
print >>sys.stderr, 'empezando a levantar %s puerto %s' % Cliente_address
sock.bind(Cliente_address)

sock.listen(1)

while True:
    # Esperando conexion
    print >>sys.stderr, 'Esperando para conectarse'
    connection, client_address = sock.accept()
 
    try:
        print >>sys.stderr, 'concexion desde', client_address
 
        # Recibe los datos en trozos y reetransmite
        while True:
            data = connection.recv(1000)
            if data: 
                print >>sys.stderr, 'recibido "%s"' % data

            else:
                print >>sys.stderr, 'se acabo'
                break

            connection.send("Jola")

    finally:
        # Cerrando conexion
        connection.close()