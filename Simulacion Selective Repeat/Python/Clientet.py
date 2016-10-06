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
	recibidoACK = False

	#while time.time() < espera + timeout:
	ready = select.select([sock], [], [], timeout)
	if ready[0]:
		data = sock.recv(1000)
		print >>sys.stderr, 'recibido "%s"' % data
		recibidoACK = True
		#data = sock.recv(19)
		#if data: 
		#	print >>sys.stderr, 'recibio'
	else:
		print >>sys.stderr, 'no recibio'

	if recibidoACK == False: 
		print >>sys.stderr, 'Timeout'	
	
	else:
		recibidoACK = False
		print >>sys.stderr, 'No hubo timeout'	

finally:
    print >>sys.stderr, 'cerrando socket'
    sock.close()