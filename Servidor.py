#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys

#Revisa que el numero de secuencia se encuntra dentro de los que está aceptando la ventana.
def checkSeq(window,seqNumber):
	resultado = False	
	for i in window:
		if i == int(seqNumber):
			resultado = True
			break
	return resultado

#Mueve la ventana un espacio.
def updateSeq(window,windowSize,recvFlags):
	for i in range(0,len(window)): #A cada númer de la ventana
		if window[i] != windowSize*2-1: # Si es distinto al máximo número de secuencia, le aumenta 1.
			window[i] += 1
		else: # Sino lo pone en cer, que sería el siguiente número de secuencia.
			window[i] -= windowSize*2-1
	recvFlags[window[len(window)-1]] = False #Pone en false, el nuevo número de secuencia metido a la ventana.

#Inicializa la ventana de 0 al máximo número de secuencia.
def initWindow(window,windowSize):
	for i in range(0,windowSize):
		window.append(i)

#Recibe el dato proveniente del Intermediario.
def recvData(connection):
	data = connection.recv(3)
	if modo == "d":
		print >>sys.stderr, 'recibido "%s"' % data
	return data

#Concatena a la hilera final, todos los caracteres que haya aceptado, antes de que se pudiera mover la ventana. (Mantener orden del mensaje)
def concatCharacter(completeData,recvCharacter):
	indexToClean = [] #Vector con todos los indices de los caracteres que ya se concatenaron a la hilera.
	for i in range(0,len(recvCharacter)):
		seqStored = recvCharacter[i].split(":")[0] #Obtiene el número de secuencia.
		dataStored = recvCharacter[i].split(":")[1] #Obtiene el caracter
		if not checkSeq(window,int(seqStored)): #Si la secuencia ya no está en la ventana, significa que se pueden copiar de manera ordenada.
			completeData += dataStored
			indexToClean.append(i)
	cleanList(recvCharacter,indexToClean)
	return completeData

#Limpia la lista de los caracteres que ya fueron concatenados a la hilera final.
def cleanList(recvCharacter,indexToClean):
	for index in sorted(indexToClean, reverse=True):
		del recvCharacter[index]
	
#Inicializa el vector que va a contener las banderas de recibido, según el número de secuencia.
def initRecvFlags(recvFlags,windowSize):
	for i in range(0,windowSize*2):
		recvFlags.append(False)

#Mueve la ventana todo lo que pueda.
def moveWindow(index,recvFlags,window,windowSize):
	while True:	 #En caso de que se haya recibido datos que no eran el primero de la ventana
		if index < len(recvFlags) and recvFlags[index]:	
			updateSeq(window,windowSize,recvFlags) #Mueve la ventana todo lo que pueda.
			index += 1
		else:
			break


if len(sys.argv) > 3:

	# Creando el socket TCP/IP
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#Asignación de argumentos.
	try:
		puertoEscucha = int(sys.argv[1]) #Puerto indicado por el Usuario, en el cual va a escuchar el Servidor.
		windowSize = int(sys.argv[2]) #Tamaño de la ventana del Servidor.
		modo = sys.argv[3] #El modo en que desea ejecutar al Servidor.
		if modo == "d" or modo == "n":
 			pass
		else:
			print "Indique el modo de ejecución con n o d únicamente"
			raise Exception()
	except Exception:
		print "Datos inválidos, asegúrese de que esta dando bien los datos como se indica. Ejecute \"python Servidor.py\" para ver que parametros se ocupan."
		sys.exit(0)
		
	window = [] #Ventana con los respectivos números de secuencia.
	recvCharacter = [] #Vector con los caracteres recibidos, para luego copiarlos en orden.
	initWindow(window,windowSize) #Inicializa la ventana.
	recvFlags = [] #Vector de banderas que indican cuales números de secuencia se han recibido.
	initRecvFlags(recvFlags,windowSize) #Inicializa el vector de banderas.
	seqMaxLen = len(str(windowSize*2-1))

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
						recvFlags[int(seqRecv)] = True #Indica el número de secuencia que fue aceptado.
						if modo == "d":
							print "Enviando ACK"+ seqRecv +" de vuelta al cliente"
						connection.sendall(seqRecv+":ACK") #Envía el ACK correspondiente al paquete recibido.
						if window[0] == int(seqRecv): #En caso de recibir el primer elemento de la ventana, esta se mueve.
							moveWindow(int(seqRecv),recvFlags,window,windowSize) #Mueve la ventana todo lo que pueda.
							completeData += dataRecv #Concatena el caracter recibido, que va antes que todos los guardados previos, si los hay.
							completeData = concatCharacter(completeData,recvCharacter) #Concatena en orden el resto de caracteres guardados.
						else:
							if data not in recvCharacter:
								recvCharacter.append(data) #Guarda el caracter recibido en el orden correspondiente.
					else:
						if recvFlags[int(seqRecv)]:
							if modo == "d":
								print "Reenviando ACK"+ seqRecv +" de vuelta al cliente"
							connection.sendall(seqRecv+":ACK") #Reenvía el ACK correspondiente al paquete recibido, que ya había sido aceptado.
						else:
							if modo == "d":
								print "%s descartado, número de secuencia inválido" %data
				else:
					if modo == "d":
						print 'no hay mas datos', client_address
					break
		finally:
			connection.close() #Cierra la conexion.
			break
	output.write(completeData) #Escribe en el archivo de salida todo el mensaje.
	print "El archivo ha sido recibido completamente"
else:
	print "Debe indicar el puerto de escucha del servidor, el tamaño de la ventana y el modo de ejecución (n o d).\nEj: python Servidor.py 10000 3 n"
