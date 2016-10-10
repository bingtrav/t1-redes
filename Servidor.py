#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys

def checkSeq(window,seqNumber):
	resultado = False	
	for i in window:
		if i == int(seqNumber):
			resultado = True
			break
	return resultado

def updateSeq(window,windowSize,recvFlags):
	for i in range(0,len(window)):
		if window[i] != windowSize*2-1:
			window[i] += 1
		else:
			window[i] -= windowSize*2-1
	recvFlags[window[len(window)-1]] = False

def initWindow(window,recvCharacter,windowSize):
	for i in range(0,windowSize):
		window.append(i)
		recvCharacter.append("")

def recvData(connection):
	data = connection.recv(3)
	if modo == "d":
		print >>sys.stderr, 'recibido "%s"' % data
	return data


def writeData(output,completeData):
	output.write(completeData)

def storeCharacter(recvCharacter,seqRecv,dataRecv,window):
	index = window.index(int(seqRecv))
	recvCharacter[index] = dataRecv

def sumCounter(recvCounter,windowSize):
	if recvCounter < windowSize-1:
		recvCounter += 1
	else:
		recvCounter = 1
	return recvCounter

def concatCharacter(completeData,recvCounter,recvCharacter,output):
	for i in range(0,recvCounter+1):
		completeData += recvCharacter[i]
		#output.write(recvCharacter[i])
		recvCharacter[i] = ""

def initRecvFlags(recvFlags,windowSize):
	for i in range(0,windowSize*2):
		recvFlags.append(False)
	

if len(sys.argv) > 3:

	# Creando el socket TCP/IP
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#Asignación de argumentos.
	puertoEscucha = int(sys.argv[1]) #Puerto indicado por el Usuario, en el cual va a escuchar el Servidor.
	windowSize = int(sys.argv[2]) #Tamaño de la ventana del Servidor.
	modo = sys.argv[3] #El modo en que desea ejecutar al Servidor.
		
	window = [] #Ventana con los respectivos números de secuencia.
	recvCharacter = [] #Vector con los caracteres recibidos, para luego copiarlos en orden.
	initWindow(window,recvCharacter,windowSize) #Inicializa la ventana y el vector de caracteres.
	recvCounter = 0 #Contador de caracteres recibidos, aceptados por la ventana, pero con los que no se puede mover la ventana aún.
	recvFlags = []
	initRecvFlags(recvFlags,windowSize)

	# Enlace de socket y puerto
	server_address = ('localhost', puertoEscucha)
	if modo == "d":
		print 'Levantando el puerto %s %s' % server_address
	sock.bind(server_address)

	# Escuchando conexiones entrantes
	sock.listen(1)
	
	#Archivo donde se va a escribir los "paquetes" que le llegan.
	output = open("Salida.txt","w")

	#Hilera que va a contener el mensaje de todos los paquetes para luego escribirlo en el archivo de salida.
	completeData = ""	

	while True:
		# Esperando conexion
		if modo == "d":
			print 'Esperando para conectarse'
		connection, client_address = sock.accept()

		if modo == "d":
			print 'Conectado a ', client_address
	 
		try:
			while True:
				data = recvData(connection)
				if data:
					seqRecv = data.split(":")[0] #Obtiene el número de secuencia.
					dataRecv = data.split(":")[1] #Obtiene el caracter					
					if checkSeq(window,seqRecv): #Revisa que el número de secuencia recibido se encuentre en la ventana.
						recvFlags[int(seqRecv)] = True
						if modo == "d":
							print "Enviando ACK"+ seqRecv +" de vuelta al cliente"
						connection.sendall(seqRecv+":ACK") #Envía el ACK correspondiente al paquete recibido.
						if window[0] == int(seqRecv): #En caso de recibir el primer elemento de la ventana, esta se mueve.
							completeData += dataRecv #Concatena el caracter recibido, que va antes que todos los guardados previos, si los hay.
							#output.write(dataRecv)
							concatCharacter(completeData,recvCounter,recvCharacter,output) #Concatena en orden el resto de caracteres guardados.
							index = int(seqRecv)
							while True:	
								if index < len(recvFlags) and recvFlags[index]:			
									updateSeq(window,windowSize,recvFlags) #Mueve la ventana todo lo que pueda.
									index += 1
								else:
									break
							recvCounter = 0 #Restablece el conteo de caracteres recibidos sin que se pudiera mover la ventana.
						else:
							storeCharacter(recvCharacter,seqRecv,dataRecv,window) #Guarda el caracter recibido en el orden correspondiente.
							recvCounter = sumCounter(recvCounter,windowSize) #Aumenta la cantidad de caracteres recibidos.
					else:
						if modo == "d":
							print "%s descartado, número de secuencia inválido" %data
				else:
					if modo == "d":
						print 'no hay mas datos', client_address
					break
		finally:
		    # Cerrando conexion
			connection.close()
			break
	output.write(completeData)
else:
	print "Debe indicar el puerto de escucha del servidor, el tamaño de la ventana y el modo de ejecución (n o d).\nEj: python Servidor.py 10000 3 n"
