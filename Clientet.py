#!/usr/bin/python

import time
import sys
import socket
import select

ventana = 5
archivo = "Hello-World. Hola mundo"
puerto = 10000
modo = 1
timeout = 3
pos = 0
posActualArchivo = 0	#donde estoy en el archivo original
tamanoSec = ventana * 2
posEnviar = 0	#posicion a enviar en la ventana
timeouts = [False for i in range(0,tamanoSec)]	#maneja los timeouts de cada paquete
array = [False for i in range(0,tamanoSec)]		#controla los acks recibidos
caracteresEnviados = 0
posInicialVentana = 0	#posicion inicial de la ventana
cantidadMovida = 0		#cuanto se mueve la ventana
posActualizar = 0
archivoTerminado = False
archivoTerminadoDeMandar = False
controladorEnviados = [False for i in range(0,tamanoSec)]	#maneja cuales posiciones han sido enviadas

#tamano de la secuencia a enviar, de ella se enviara uncamente la ventana.
bufferSecuencia = [None]*(tamanoSec)

def EntradaDatos():#metodo encargado de recuperar los inputs
	global ventana 
	global archivo
	global puerto
	global modo
	global timeout
	ventana = int(input('Digite el tamano de la ventana:'))
	archivo = str(raw_input('Digite el archivo a enviar:'))
	puerto =  int(input('Digite el puerto del cliente:'))
	modo = int(input('Digite 0 para modo normal, 1 para modo debug:'))
	timeout = input('Digite el tiempo de timeout:')

#EntradaDatos()#si se comenta el metodo se utilizaran valores por defecto
#creacion del socket y conexion
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
server_address = ('localhost', puerto)
print >>sys.stderr, 'conectando a %s puerto %s' % server_address
sock.connect(server_address)
#sock.setblocking(0)		



def print_debug(data):
	if(modo == 1):
		print(data)

#llena el buffer con los caracteres que siguen del archivo
def llenarBufferSecuencia():
	global posActualArchivo
	for letra in range(0, tamanoSec):
		bufferSecuencia[letra] = archivo[posActualArchivo]
		posActualArchivo += 1 	
		#print_debug (bufferSecuencia[letra])
	
    	#print_debug (posActualArchivo)

#actualiza el buffer de secuencia con nuevos datos para ser enviados
#lo que esta a la izquierda de la ventana se puede descartar y actualizar
#posInicial representa es la posicion donde inicia la ventana, o sea, posEnviar
def actualizarBuffer(posInicial):
	global archivoTerminado
	global controladorEnviados
	global posActualArchivo
	global posActualizar

	if posActualArchivo >= len(archivo):
		archivoTerminado = True
		#print_debug('arch ter')
		#print_debug(archivoTerminado)

	i = 0
	while i < cantidadMovida:		#actualiza las posiciones que ya tienen ack
		if posActualArchivo < len(archivo):
			bufferSecuencia[posActualizar] = archivo[posActualArchivo]
			controladorEnviados[posActualizar] = False		#resetea la posicion a no enviada
			posActualArchivo += 1 	
			posActualizar += 1
			if posActualizar >= tamanoSec:
				posActualizar = 0
		i += 1

    	#print_debug (posActualArchivo)
		#print_debug(bufferSecuencia)

#determina el numero de posiciones que la ventana se debe mover a la derecha
#pos es la posicion donde inicia la ventana, o sea, posInicialVentana
def moverVentana(pos):
	#print_debug('pos ventana')
	#print_debug(pos)
	global posInicialVentana
	global cantidadMovida
	global caracteresEnviados
	global posEnviar
	global array

	cantidadMovida = 0
	acks = 0
	i = 0
	while i < ventana and array[pos] == True:	#cuenta cuantos acks se han recibido seguidos
		acks += 1
		array[pos] = False		#resetea la bandera del ack de la posicion
		pos += 1
		if pos >= tamanoSec:
			pos = 0
		i += 1

	posInicialVentana += acks	#corre la ventana el numero de acks recibidos
	caracteresEnviados += acks 	#aumenta el numero de caracteres enviados
	cantidadMovida += acks
	if posInicialVentana >= tamanoSec:	#que sea ciclico
		posInicialVentana = posInicialVentana % tamanoSec

	posEnviar = posInicialVentana 	#actualiza la nueva posicion a mandar

#reenvia los paquetes que estan en pos
def reenviar(pos):
	print_debug("Reenviando paquete " + str(pos))
	try:
		dato = str(str(pos)+ ':' + str(bufferSecuencia[pos])) + '\n'
		sock.send(dato)
		timeouts[pos] = time.time()
	finally:
		pass

def CheckTimeout(posInicial):
	#print_debug('verificando Timeout...')
	global ventana
	global tamanoSec
	i = 0
	while i < ventana:
		if timeouts[posInicial] + timeout < time.time():
			print_debug("Vencio timeout de paquete: " + str(i))
			reenviar(posInicial)
		posInicial += 1
		if posInicial >= tamanoSec:
			posInicial = 0
		i+=1

#Loop de cliente
try:
	primeraCorrida = True
	i = 0
	llenarBufferSecuencia()

	while caracteresEnviados < len(archivo):
		k = 0

		if primeraCorrida == False and archivoTerminado == False:
			actualizarBuffer(posInicialVentana)

		while k < ventana and archivoTerminadoDeMandar == False:		#mientras hayan datos por enviar en la ventana
			if archivoTerminado == True:
				archivoTerminadoDeMandar == True

			if controladorEnviados[posEnviar] == False:
				dato = str(str(posEnviar)+ ':' + str(bufferSecuencia[posEnviar])) + '\n' #envia el numero de paquete y el caracter difinido en esa posicion
				print_debug("Enviando segmento:" + dato)
				sock.send(dato)
				controladorEnviados[posEnviar] = True
				timeouts[posEnviar] = time.time()	#se pone el timeout del dato recien enviados
				
			posEnviar += 1
			if posEnviar >= tamanoSec:	#para que circule
				posEnviar = 0
			k += 1
		
		ready = select.select([sock], [], [], 1)
		
		if ready[0]: #si puede recibir
			servidor_response = sock.recv(1) #recibe el ack del intermediario 
		else: #sino recibio nada, pone la respuesta en null
			servidor_response = None 

		if servidor_response: #si hay respuesta 
			rec =''
			while servidor_response and servidor_response !='\n':
				rec += 	servidor_response
				servidor_response = sock.recv(1)	
			servidor_response = rec
			ack = int(servidor_response)	#guarda el ack
			if array[ack] == False:		#si todavia no ha llegado ese ack
				print_debug("Recibiendo ack:" + str(servidor_response))
				array[ack] = True
		
		moverVentana(posInicialVentana)		#mueve el valor de la posicion incial de la ventana al primero que esta en False
		CheckTimeout(posInicialVentana)
		primeraCorrida = False

finally:
	print("Concluyo la transferencia del archivo")
	print >>sys.stderr, 'cerrando socket'
	sock.close()