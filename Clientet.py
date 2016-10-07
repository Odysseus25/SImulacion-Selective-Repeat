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
array = [False for i in range(0,ventana)]


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
server_address = ('localhost', puerto)
print >>sys.stderr, 'conectando a %s puerto %s' % server_address
sock.connect(server_address)
sock.setblocking(0)				

try:
	
	i = 0

	while i < ventana:
		dato = str((i,':',archivo[pos]))
		print dato
		sock.send(dato)
		pos += 1
		i += 1 

	espera =  time.time()

	j = 0
	while time.time() < espera + timeout and j < ventana:
		ready = select.select([sock], [], [], timeout)
		if ready[0]:
			data = sock.recv(13)
			if data: 
				#
				index = int(data[10])
				if array[index] == False:	
					print >>sys.stderr, 'llego "%s"'% data[10]	
					array[index] = True
					j += 1
		#if (data[4]): 
		#print >>sys.stderr, 'recibio'
	#ready = select.select([sock], [], [], timeout)
	#if ready[0]:
	#	data = sock.recv(13)
	#	print >>sys.stderr, 'recibido "%s"' % data
	#	recibidoACK = True
		#data = sock.recv(19)
		#if data: 
		#	print >>sys.stderr, 'recibio'
	else:
		print >>sys.stderr, 'no recibio'

	if j < ventana: 
		print >>sys.stderr, 'Timeout'	
	
	else:
		print >>sys.stderr, 'No hubo timeout'	

finally:
    print >>sys.stderr, 'cerrando socket'
    sock.close()