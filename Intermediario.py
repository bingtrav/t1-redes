#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import time
import socket
import sys
import numpy as np

def checkSeq(window,seqNumber): #Revisa que el número de secuencia dado, se encuentra en la ventana actual.
	resultado = False	
	for i in window:
		if i == int(seqNumber):
			resultado = True
			break
	return resultado

def initWindow(window,windowSize): #Inicializa la ventana
	for i in range(0,windowSize):
		window.append(i)

def initFlags(recvFlags,windowSize): #Inicializa el vector de banderas de recibidos.
	for i in range(0,windowSize*2):
		recvFlags.append(False)

def moveWindow(index,recvFlags,window,windowSize):
	while True:	 #En caso de que se haya recibido datos que no eran el primero de la ventana
		if index < len(recvFlags) and recvFlags[index]:	
			updateSeq(window,windowSize,recvFlags) #Mueve la ventana todo lo que pueda.
			index += 1
		else:
			break

#Mueve la ventana un espacio.
def updateSeq(window,windowSize,recvFlags):
	for i in range(0,len(window)): #A cada númer de la ventana
		if window[i] != windowSize*2-1: # Si es distinto al máximo número de secuencia, le aumenta 1.
			window[i] += 1
		else: # Sino lo pone en cer, que sería el siguiente número de secuencia.
			window[i] -= windowSize*2-1
	recvFlags[window[len(window)-1]] = False #Pone en false, el nuevo número de secuencia metido a la ventana.



class thread (threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name

	def run(self):
		listenAndSend(self.threadID,self.name)

def listenAndSend(threadID,threadName):
	#Variables compartidas definidas en el hilo principal.
	global sockListenClient
	global sockSendServer
	global connection
	global serverSocketClosed
	global mode
	global prob
	global answerToDelete
	global recvFlags
	global packagesToIgnore
	global window
	global windowSize
	delete = "n" #Indicador si un paquete se debe de eliminar o no
	packetCounter = -1 #Contador secuencial de paquetes enviados por el Cliente

	if threadID == 1: #Hilo encargado de escuchar al cliente y enviar al servidor.
		while True:
			# Esperando conexion
			if mode == "d":
				print 'Esperando para conectarse'
			connection, client_address = sockListenClient.accept()
		 
			try:
				if mode == "d":
					print 'Conexion desde', client_address
		 
				while True:
					data = connection.recv(3)
					if mode == "d":
						print 'Recibido "%s"' % data
					if data:
						if answerToDelete == "s": #En caso de que haya elegido eliminar paquetes manualmente.
							seqRecv = data.split(":")[0]
							if checkSeq(window,seqRecv): #Va moviendo la ventana conforme va recibiendo los paquetes, al igual que en el Servidor.
								recvFlags[int(seqRecv)] = True
								packetCounter += 1 #Solamente suma el numero de "paquete" por el que va, si es uno nuevo y no una retransmisión.
								if window[0] == int(seqRecv):
									moveWindow(int(seqRecv),recvFlags,window,windowSize)
							if str(packetCounter) in packagesToIgnore: #Pregunta si por el paquete que va, es uno de los que debe de eliminar
								packagesToIgnore.remove(str(packetCounter))  #Si sí debe eliminarlo, lo borra de la lista de paquetes a eliminar.
								delete = "s" #E indica que hay que descartar ese paquete.
							else:
								delete = "n"#De manera contraria especifica que no hay que descartarlo.
						try:
							if delete == "s": #Pregunta si el paquete hay que descartarlo.
								if mode == "d":
									print ('\x1b[0;37;41m'+ "Paquete \"perdido\" (%s)" % data + '\x1b[0m')
							else: #Si no hay que descartarlo
								if np.random.choice(np.arange(0,2), p=[prob,1-prob]): #Realiza la probablidad de pérdida, con la proba dada.
									if mode == "d": 
										print 'Enviando mensaje al servidor'
									sockSendServer.sendall(data)
								else:
									print ('\x1b[0;37;41m'+ "Paquete \"perdido\" (%s)" % data + '\x1b[0m')
						finally:
							pass
					else:
						if mode == "d":
							print 'No hay mas datos', client_address
							print 'Cerrando socket que envía al servidor'
						sockSendServer.close()
						serverSocketClosed = True
						break
			finally:
				connection.close()
				break
		
		
	elif threadID == 2: #Hilo encargado de escuchar al servidor y enviar al cliente.
		sockSendServer.settimeout(1.0)
		while not serverSocketClosed:
			while True:
				try:
					serverResponse = sockSendServer.recv(5) #Escucha la respuesta del Servidor.
					if mode == "d":
						print 'Recibiendo "%s"' % serverResponse
						print 'Enviando mensaje de vuelta al cliente'
					connection.sendall(serverResponse) #La envía al Cliente.
				finally:
					break
		

if len(sys.argv) > 4:
	
	try:
		clientAddress = int(sys.argv[1])
		serverAddress = int(sys.argv[2])
		prob = float(sys.argv[3])
		mode = sys.argv[4]
		if mode == "n" or mode == "d":
			pass
		else:
			print "Indique el modo de ejecución con n o d únicamente"
			raise Exception()
	except Exception:
		print "Datos inválidos, asegúrese de que esta dando bien los datos como se indica. Ejecute \"python Intermediario.py\" para ver que parametros se ocupan."
		sys.exit(0)


	answerToDelete = "n"
	window = []
	windowSize = 0
	packagesToIgnore = []
	recvFlags = []

	if mode == "d":
		while True:
			answerToDelete = raw_input("Desea eliminar paquetes? [s/n] : ")# Pregunta si desea eliminar paquetes manualmente.
			if answerToDelete == "s" or answerToDelete == "n":
				break
			else:
				print "Respuesta inválida indique s o n"
		if answerToDelete == "s": 
			while True:
				try:
					windowSize = int(raw_input("Tamaño ventana : "))
					packagesToIgnore = raw_input("Indique los números de paquete a eliminar de la forma x,y,z (Deben ser números válidos entre 0 y tamaño del archivo): ").split(",")
					break
				except Exception:
					print "Datos inválidos, asegúrese de que esta dando bien los datos."
	initWindow(window,windowSize)
	initFlags(recvFlags,windowSize)

	# Creando el socket TCP/IP
	sockListenClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockSendServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Enlace de socket y puerto
	intermediario_address = ('localhost', clientAddress)
	if mode == "d":
		print 'Empezando a levantar %s puerto %s' % intermediario_address
	sockListenClient.bind(intermediario_address)

	# Conecta el socket en el puerto cuando el servidor esté escuchando
	server_address = ('localhost', serverAddress)
	if mode == "d":
		print 'Conectando a %s puerto %s' % server_address
	sockSendServer.connect(server_address)

	# Escuchando conexiones entrantes
	sockListenClient.listen(1)

	connection = None
	serverSocketClosed = False 

	# Creación de los threads
	thread1 = thread(1, "clientListener")
	thread2 = thread(2, "serverListener")

	# Inicio de los threads
	thread1.start()
	thread2.start()
else:
	print "Debe indicar\n1.El puerto donde escucha al cliente\n2.El puerto donde espera el servidor\n3.La probabilidad de pérdidad de paquetes\n4.El modo de ejecución [d/n]\nEj: python Intermediario.py 10001 10000 0.05 n"
