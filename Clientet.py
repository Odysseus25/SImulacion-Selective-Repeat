#!/usr/bin/python

import time
import sys
import socket
import select

cantidad= len(sys.argv)
#if cantidad > 1: 
	#ventana = sys.argv[1]	
	#if cantidad > 2: 
	#	archivo = sys.argv[2]
	#	if cantidad > 3: 
	#		puerto  = int(sys.argv[3])
	#		if cantidad > 4: 
	#			modo = sys.argv[4]
	#			if cantidad > 5: 
	#				timeout = sys.argv[5]

ventana = 5
archivo = "Hello-World"
puerto = 10000
modo = 0
timeout = 3
pos = 0
posActualArchivo = 0	#donde estoy en el archivo original
tamanoSec = ventana * 2
posEnviar = 0	#posicion a enviar en la ventana
timeouts = [False for i in range(0,tamanoSec)]
array = [False for i in range(0,tamanoSec)]
caracteresEnviados = 0
posInicialVentana = 0

#tamano de la secuencia a enviar, de ella se enviara uncamente la ventana.
bufferSecuencia = [None]*(tamanoSec)

#creacion del socket y conexion
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
server_address = ('localhost', puerto)
print >>sys.stderr, 'conectando a %s puerto %s' % server_address
sock.connect(server_address)
#sock.setblocking(0)		


#llena el buffer con los caracteres que siguen del archivo
def llenarBufferSecuencia():
	global posActualArchivo
	for letra in range(0, tamanoSec):
		bufferSecuencia[letra] = archivo[posActualArchivo]
		posActualArchivo += 1 	
		print (bufferSecuencia[letra])
	
    	print (posActualArchivo)

#actualiza el buffer de secuencia con nuevos datos para ser enviados
#lo que esta a la izquierda de la ventana se puede descartar y actualizar
#posInicial representa es la posicion donde inicia la ventana, o sea, posEnviar
def actualizarBuffer(posInicial):
	global posActualArchivo
	inicio = (posInicial + ventana) % tamanoSec		#define de donde a donde actualizar el buffer
	i = 0
	while i < ventana:
		bufferSecuencia[inicio] = archivo[posActualArchivo]
		posActualArchivo += 1 	
		inicio += 1
		i += 1
		print (bufferSecuencia[inicio])
	
    	print (posActualArchivo)

#determina el numero de posiciones que la ventana se debe mover a la derecha
#pos es la posicion donde inicia la ventana, o sea, posInicialVentana
def moverVentana(pos):
	global posInicialVentana
	global caracteresEnviados
	global posEnviar
	acks = 0
	i = 0
	while i < ventana and array[pos] == True:	#cuenta cuantos acks se han recibido seguidos
		acks += 1
		pos += 1
		i += 1
	posInicialVentana += acks	#corre la ventana el numero de acks recibidos
	caracteresEnviados += acks 	#aumenta el numero de caracteres enviados
	if posInicialVentana >= tamanoSec:	#que sea ciclico
		posInicialVentana = posInicialVentana % tamanoSec
	posEnviar = posInicialVentana 	#actualiza la nueva posicion a mandar

#reenvia los paquetes que estan en pos
def reenviar(pos):
	try:
		dato = str((pos,':',bufferSecuencia[pos]))
		sock.send(dato)
	finally:
		print >>sys.stderr, 'paquete reenviado'

def CheckTimeout(posInicial, posFinalVentana):
	i = posInicial
	while i < posFinalVentana:
		if timeouts[i] + timeout < time.time():
			reenviar(i)
		i+=1

#Loop de cliente
try:
	primeraCorrida = True
	i = 0
	llenarBufferSecuencia()

	while caracteresEnviados < len(archivo):
		k = 0

		while k < ventana:		#mientras hayan datos por enviar en la ventana
			dato = str(str(posEnviar)+ ':' + str(bufferSecuencia[posEnviar])) + '\n' #envia el numero de paquete y el caracter difinido en esa posicion
			print dato
			sock.send(dato)
			timeouts[posEnviar] = time.time()	#se pone el timeout del dato recien enviados
			posEnviar += 1
			if posEnviar >= tamanoSec:	#para que circule
				posEnviar = 0
			k += 1

		#ready = select.select([sock], [], [], timeout)	#si se puede recibir
		#if ready[0]:
			servidor_response = sock.recv(1) #recibe el ack del intermediario 
			if servidor_response: #si hay respuesta 
				rec =''
				while servidor_response and servidor_response !='\n':
					rec += 	servidor_response
					servidor_response = sock.recv(1)

				servidor_response = rec
				ack = int(servidor_response)	#guarda el ack
				if array[ack] == False:		#si todavia no ha llegado ese ack
					print >> sys.stderr, 'llego "%s"' %servidor_response
					array[ack] = True
					moverVentana(posInicialVentana)		#mueve el valor de la posicion incial de la ventana al primero qyue esta en False

		CheckTimeout(posInicialVentana, ventana)
		primeraCorrida = False

finally:
	print >>sys.stderr, 'cerrando socket'
	sock.close()