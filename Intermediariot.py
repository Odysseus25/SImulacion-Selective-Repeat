
import socket
import sys
import random
import threading
import thread

port_cliente = 10000; 
port_servidor = 10001; 

modo = 0
proba_perdida = 20 #Numero entre 0 y cien
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Cliente_address = ('localhost', port_cliente)
servidor_address = ('localhost', port_servidor)
stringCheckDescarte = "" #string que contendra todos los paquetes a descartar
stringCheckDescarteAck = "" #string que contendra todos los ack a descartar

def EntradaDatos(): #metodo encargado de recuperar los inputs
    global port_cliente
    global port_servidor
    global proba_perdida
    global modo
    port_cliente =  int(input('Digite el puerto del Cliente:'))
    port_servidor =  int(input('Digite el puerto del servidor:'))
    proba_perdida = int(input('Digite un numero del 0 a 100 representante de la proba de perdida:'))
    modo = int(input('Digite 0 para modo normal, 1 para modo debug:'))


#EntradaDatos() #si se comenta el metodo se utilizaran valores por defecto

def getSec(data): #metodo encargado de devolver la secuencia de un paquete
    i =0
    sec =''
    while i < len(data) and data[i] != ':':
        sec += data[i]
        i+=1
    return sec

def input_descarte(): #input de los paquetes que el usuario desee descartar, se escriben los numeros seguidos por una coma
    global stringCheckDescarte
    if(modo == 1):
        try:
            stringCheckDescarte = str(input('Cuales paquetes desea descartar(digite los paquetes, seguidos por una coma para poner el siguiente):'))
        except Exception as e:
            pass




def input_descarteAck(): #input de los acks que el usuario desee descartar, se escriben los numeros seguidos por una coma
    global stringCheckDescarteAck 
    if(modo == 1):
        try:
            stringCheckDescarteAck = str(input('Cuales ack desea descartar(digite los ack, seguidos por una coma para poner el siguiente):'))
        except Exception as e:
            pass

def CheckDescarte(num): #metodo encargado de buscar en la lista de paquetes a descartar, si el paramtro de entrada existe en la lista o no
    global stringCheckDescarte
    pos = 1
    paquete = ''

    while pos < (len(stringCheckDescarte) -1):  #mientras se pueda mover por la lista
        paquete = '' #limpia la variable auxiliar
        while(pos < (len(stringCheckDescarte) -1) and stringCheckDescarte[pos] != ','):#mientras no sea el final de la lista o haya una coma
            if len(paquete) == 1 and paquete[0] == ' ': #si el paquete esta en limpio (esto se hizo porque sino salia con un espacio de mas)
                paquete = stringCheckDescarte[pos]#se anade el caracter a la variable auxiliad
            else:
                paquete += stringCheckDescarte[pos]
            pos+=1#se aumenta la pos
        pos +=1 #si pos esta sobre una coma, obviela
        if(paquete == num): #si se encontro el numero dentro de la lista de eliminados, devuelve true
            return True
        del paquete #limpia el paquete

    return False


def CheckDescarteAck(num): #metodo encargado de buscar en la lista de paquetes a descartar, si el paramtro de entrada existe en la lista o no
    global stringCheckDescarte
    pos = 1
    paquete = ''

    while pos < (len(stringCheckDescarteAck) -1): #mientras se pueda mover por la lista
        paquete = '' #limpia la variable auxiliar
        while(pos < (len(stringCheckDescarteAck) -1) and stringCheckDescarteAck[pos] != ','):#mientras no sea el final de la lista o haya una coma
            if len(paquete) == 1 and paquete[0] == ' ': #si el paquete esta en limpio (esto se hizo porque sino salia con un espacio de mas)
                paquete = stringCheckDescarteAck[pos]#se anade el caracter a la variable auxiliad
            else:
                paquete += stringCheckDescarteAck[pos]
            pos+=1#se aumenta la pos
        pos +=1 #si pos esta sobre una coma, obviela
        if(paquete == num): #si se encontro el numero dentro de la lista de eliminados, devuelve true
            return True
        del paquete #limpia el paquete

    return False


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
                if modo == 1:
                    sec = str(getSec(data))
                    valor = CheckDescarte(sec)
                    if (valor == True): #si la secuencia del paquete esta en la lista por descartar
                        print "Se descarto el paquete: "+ str(data)  # se descarta
                    else:
                        sock_servidor.send(data+'\n') #sino se envia
                else:
                    ran = random.randint(1, 100) #se busca un numero random entre 1 y 100, de ser mayor al numero de proba de perdida se envia 
                    if ran > proba_perdida:  
                            sock_servidor.send(data+'\n')
                    else:
                            print "Se descarto el paquete: "+ str(data)    
            else:
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
            if modo == 1: #si se esta en modo debug
                if CheckDescarteAck(data): #si el ack esta en la lista por descartar
                    print "Se descarto el ack: "+ str(data) # se descarta
                else:
                    connection.send(data + '\n') #sino se envia

            else:
                ran = random.randint(1, 100) #se busca un numero random entre 1 y 100, de ser mayor al numero de proba de perdida se envia 
                #print >>sys.stderr, 'ran = "%s"' % ran
                if ran > proba_perdida:  
                    #print >>sys.stderr, 'enviando ack al cliente "%s"' % data
                    connection.send(data + '\n')
                else:
                    print "Se descarto el ack: "+ str(data)     
           
input_descarte()
input_descarteAck()

print "Creada conexion con el Servidor en puerto: "+ str(port_servidor)
sock_servidor.connect(servidor_address)
sock.bind(Cliente_address)
sock.listen(1)
print "Creada conexion con el Cliente en puerto: "+ str(port_cliente)



while True:
    connection, client_address = sock.accept()
 
    try:
        thread.start_new_thread(SendData, ())
        thread.start_new_thread(ReceiveData, ())

    finally:
        # Cerrando conexion
        pass
        #connection.close()