#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import time
import socket
import sys
import numpy as np

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
	global desireToDelete
	packetCounter = 0 #Contador de paquetes secuencial, en caso de que el usuario haya seleccionado eliminar alguno.

	if threadID == 1: #Hilo encargado de escuchar al cliente y enviar al servidor.
		while True:
			# Esperando conexion
			if mode == "d":
				print 'Esperando para conectarse'
			connection, client_address = sockListenClient.accept()
		 
			try:
				if mode == "d":
					print 'Conexion desde', client_address
		 
				# Recibe los datos en trozos y reetransmite
				while True:
					data = connection.recv(3)
					if mode == "d":
						print 'Recibido "%s"' % data
					if data:
						packetCounter += 1
						try:
							if (len(desireToDelete) > 0) and (packetCounter in desireToDelete):
								#if mode == "d":
								#	print "Paquete \"perdido\""
								print "Paquete \"perdido\""
							else:
								if np.random.choice(np.arange(0,2), p=[prob,1-prob]):
									if mode == "d":
										print 'Enviando mensaje al servidor'
									sockSendServer.sendall(data)
								else:
									if mode == "d":
										print "Paquete \"perdido\""
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
					serverResponse = sockSendServer.recv(5)
					if mode == "d":
						print 'Recibiendo "%s"' % serverResponse
						print 'Enviando mensaje de vuelta al cliente'
					connection.sendall(serverResponse)
				finally:
					break
		

if len(sys.argv) > 4:

	clientAddress = int(sys.argv[1])
	serverAddress = int(sys.argv[2])
	prob = float(sys.argv[3])
	mode = sys.argv[4]
	desireToDelete = [] #Vector que contiene todos los paquetes que el usuario desea eliminar.

	if mode == "d":
		answer = raw_input("Desea eliminar paquetes? [y/n] : ")# Pregunta si desea eliminar paquetes.
		if answer == "y": #En caso de querer hacerlo se le pide que indique los números de paquete separados por "," y que sean válidos.
			ans = raw_input("Indique los paquetes a eliminar de la forma x,y,z\nDeben ser números válidos entre 1 y tamaño del archivo: ")
			for num in ans.split(","): #Separa los números ingresados y los guarda en el vector.
				desireToDelete.append(int(num))

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
	print "Debe indicar\n1.El puerto donde escucha al cliente\n2.El puerto donde espera el servidor\n3.La probabilidad de pérdidad de paquetes\n4.El modo de ejecución\nEj: python Intermediario.py 10001 10000 0.05 n"
