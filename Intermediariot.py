
import socket
import sys
import random
import threading
import thread

port_cliente = 10000; 
port_servidor = 10001; 

proba_perdida = 0.5

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Cliente_address = ('localhost', port_cliente)
servidor_address = ('localhost', port_servidor)
sock_servidor.connect(servidor_address)


print >>sys.stderr, 'empezando a levantar %s puerto %s' % Cliente_address

sock.bind(Cliente_address)
sock.listen(1)

def SendData():
    try:
    	while True:
            data = connection.recv(1) #se reciben los datos
            rec = ''
            if data:
                while data and data != '\n':
                    rec += data
                    data = connection.recv(1) 

            data = rec
            if data:
	            print >>sys.stderr, 'recibido "%s"' % data
	            sock_servidor.send(data+'\n')
	            print >>sys.stderr, 'enviado'
            else:
	            print >>sys.stderr, 'se acabo'
	            break
    except Exception:
    	import traceback
    	print traceback.format_exc()
	            

def ReceiveData():
   while True:
        data = sock_servidor.recv(1) #se reciben los datos
        rec = ''
        if data:
            while data and data != '\n':
                rec += data
                data = sock_servidor.recv(1) 

        data = rec
        if data:
            ran = random.randint(1, 100) #se busca un numero random entre 1 y 100, de ser mayor al numero de proba de perdida se envia 
            #print >>sys.stderr, 'ran = "%s"' % ran
            if ran > proba_perdida:  
                print >>sys.stderr, 'enviando ack al cliente "%s"' % data
                connection.send(data + '\n')
            else:
                print >>sys.stderr, 'se perdio el ack "%s"' % data
        else:
            print >>sys.stderr, 'no hay mas datos', client_address        
           

while True:
    # Esperando conexion
    print >>sys.stderr, 'Esperando para conectarse'
    connection, client_address = sock.accept()
 
    try:
        print >>sys.stderr, 'concexion desde', client_address
        thread.start_new_thread(SendData, ())
        thread.start_new_thread(ReceiveData, ())
        # Recibe los datos en trozos y reetransmite
        #while True:

                #break
    finally:
        # Cerrando conexion
        pass
        #connection.close()