import socket
import sys
 
# Creando el socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ventana = 5
puerto = 10001

# Enlace de socket y puerto
intermediario = ('localhost', puerto)
print >>sys.stderr, 'empezando a levantar %s puerto %s' % intermediario
sock.bind(intermediario)

sock.listen(1)

while True:
    # Esperando conexion
    print >>sys.stderr, 'Esperando para conectarse'
    connection, client_address = sock.accept()
 
    try:
    	print >>sys.stderr, 'concexion desde', client_address
        while True:
            data = connection.recv(13)
            print >>sys.stderr, 'recibido "%s"' % data
            if data:
            	ack = "ack ", str(data[1])
                print >>sys.stderr, 'enviando ack ', ack
                connection.sendall(str(ack))
            else:
                print >>sys.stderr, 'no hay mas datos', client_address
                break



    finally:
        # Cerrando conexion
        connection.close()