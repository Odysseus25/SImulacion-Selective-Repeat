
import socket
import sys
import random

port_cliente = 10000; 
port_servidor = 10001; 

proba_perdida = 50

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Cliente_address = ('localhost', port_cliente)
servidor_address = ('localhost', port_servidor)
sock_servidor.connect(servidor_address)


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
            data = connection.recv(13)
            if data: 
                print >>sys.stderr, 'recibido "%s"' % data

            else:
                print >>sys.stderr, 'se acabo'
                break

            sock_servidor.send(data)
           
            data = sock_servidor.recv(13)
            if data:
                ran = random.randint(1, 100) #se busca un numero random entre 1 y 100, de ser mayor al numero de proba de perdida se envia 
                print >>sys.stderr, 'ran = "%s"' % ran
                if ran > proba_perdida:  
                    print >>sys.stderr, 'enviando ack al cliente "%s"' % data
                    connection.send(data)
                else:
                    print >>sys.stderr, 'se perdio el ack "%s"' % data
            else:
                print >>sys.stderr, 'no hay mas datos', client_address
                #break
    finally:
        # Cerrando conexion
        connection.close()