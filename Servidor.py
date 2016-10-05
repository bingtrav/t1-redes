#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Programa Servidor
# Fuente original de este codigo: www.pythondiario.com
# Utilizado para fines academicos en el curso CI-1320 

import socket
import sys
 
# Creando el socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


if len(sys.argv) > 3:
	#Asignación de argumentos.
	puertoEscucha = int(sys.argv[1]) #Puerto indicado por el Usuario, en el cual va a escuchar el Servidor.
	windowSize = int(sys.argv[2]) #Tamaño de la ventana del Servidor.
	modo = sys.argv[3] #El modo en que desea ejecutar al Servidor.
	#SECUENCIA TEMPORAL	
	ventana = []
	for i in range(0,windowSize):
		ventana.append(i)

	recibidos = []
	secuencia = []
	for i in range(0,8):
		secuencia.append(i)
		recibidos.append(False)

	# Enlace de socket y puerto
	server_address = ('localhost', puertoEscucha)
	if modo == "d":
		print >>sys.stderr, 'Empezando a levantar %s puerto %s' % server_address
	sock.bind(server_address)

	# Escuchando conexiones entrantes
	sock.listen(1)
	
	#Archivo donde se va a escribir los "paquetes" que le llegan.
	archivoSalida = open("Salida.txt","w")	

	while True:
		# Esperando conexion
		if modo == "d":
			print >>sys.stderr, 'Esperando para conectarse'
		connection, client_address = sock.accept()
	 
		try:
			if modo == "d":
				print >>sys.stderr, 'concexion desde', client_address
	 
		    # Recibe los datos en trozos y reetransmite
			while True:
				data = connection.recv(1000)
				if modo == "d":
					print >>sys.stderr, 'recibido "%s"' % data
				if data:
					seqRecv = data.split(":")[0]
					dataRecv = data.split(":")[1]
					#REVISA EL NUMERO DE SECUENCIA RECIBIDO EN LA VENTANA					
					resultado = False	
					for i in ventana:
						if i == int(seqRecv):
							resultado = True
							break
					if resultado:
						if modo == "d":
							print >>sys.stderr, "enviando ACK"+ seqRecv +" de vuelta al cliente"
						connection.sendall(seqRecv+":ACK")
						#Escribe mensaje recibido en el archivo "Salida.txt"
						archivoSalida.write(dataRecv)
						recibidos[int(seqRecv)] = True
						if recibidos[0]:
							if(max(ventana) != 7):
								for i in range(0,len(ventana)):
									ventana[i] += 1
							else:
								if recibidos[len(recibidos)]:
									for i in range(0,windowSize):
										ventana[i] = i
										recibidos[i] = False	
				else:
					if modo == "d":
						print >>sys.stderr, 'no hay mas datos', client_address
					break
		         
		finally:
		    # Cerrando conexion
			connection.close()
else:
	print "Debe indicar el puerto de escucha del servidor, el tamaño de la ventana y el modo de ejecución (n o d).\nEj: python Servidor.py 10000 3 n"

def checkSeq(number):
	resultado = False	
	for i in ventana:
		if i == number:
			resultado = True
			break
	return resultado

def updateSeq():
	if(max(ventana) < 19):
		for i in ventana:
			ventana[i] += 1
	else:
		for i in range(0,windowSize):
			ventana[i] = i
			recibidos[i] = False

