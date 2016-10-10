import socket
import sys
 
# Creando el socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ventana = 5
tamanoSec = ventana * 2
array = [False for i in range(0,tamanoSec)]
puerto = 10001

# Enlace de socket y puerto
intermediario = ('localhost', puerto)
print >>sys.stderr, 'empezando a levantar %s puerto %s' % intermediario
sock.bind(intermediario)

sock.listen(1)


def moverVentana(pos):
    global posInicialVentana
    acks = 0
    i = 0
    while i < ventana and array[pos] == True:   #cuenta cuantos acks se han recibido seguidos
        acks += 1
        pos += 1
        if pos >= tamanoSec:
            pos = 0
        i += 1
    posInicialVentana += acks   #corre la ventana el numero de acks recibidos
    if posInicialVentana >= tamanoSec:  #que sea ciclico
        posInicialVentana = posInicialVentana % tamanoSec


def getSec(data):
    i =0
    sec =''
    while i < len(data) and data[i] != ':':
        sec += data[i]
        i+=1
    return sec


text_file = open("MensajeRecibido.txt", "w")

posInicialVentana = 0
while True:
    # Esperando conexion
    print >>sys.stderr, 'Esperando para conectarse'
    connection, client_address = sock.accept() #se guarda en la variable connection la conexion al puerto
 
    try:
    	print >>sys.stderr, 'concexion desde', client_address
        while True:
            

            data = connection.recv(1) #se reciben los datos
            rec = ''
            if data:
                while data and data != '\n':
                    rec += data
                    data = connection.recv(1) 

            data = rec
            text_file.write(data + '\n')
            print >>sys.stderr, 'recibido "%s"' % data
            if data:
            	sec = str(getSec(data))
                if array[int(sec)] == False:
                    array[int(sec)] = True
                    moverVentana(posInicialVentana)

                print >>sys.stderr, 'enviando ack ', sec
                connection.send(str(sec)+'\n')
            else:
                print >>sys.stderr, 'no hay mas datos', client_address
                break




    finally:
        # Cerrando conexion
        text_file.close()
        connection.close()