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
		#print "Starting " + self.name
		listenAndSend(self.threadID,self.name)
		print "Exiting " + self.name

def listenAndSend(threadID,threadName):

	global sockListenClient
	global sockSendServer
	global connection
	global serverSocketClosed
	global mode
	global prob

	if threadID == 1:
		while True:
			# Esperando conexion
			print 'Esperando para conectarse'
			connection, client_address = sockListenClient.accept()
		 
			try:
				print 'Conexion desde', client_address
		 
				# Recibe los datos en trozos y reetransmite
				while True:
					data = connection.recv(3)
					print 'Recibido "%s"' % data
					if data:
						try:
							if np.random.choice(np.arange(0,2), p=[prob,1-prob]):
								print 'Enviando mensaje al servidor'
								sockSendServer.sendall(data)
							else:
								print "Paquete \"perdido\""
						finally:
							#print "Esperando respuesta del servidor"
							pass
					else:
						print 'No hay mas datos', client_address
						print 'Cerrando socket que envía al servidor'
						sockSendServer.close()
						serverSocketClosed = True
						break
			finally:
				connection.close()
				break
		
		
	elif threadID == 2:
		sockSendServer.settimeout(1.0)
		while not serverSocketClosed:
			while True:
				try:
					serverResponse = sockSendServer.recv(5)
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

	# Creando el socket TCP/IP
	sockListenClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sockSendServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Enlace de socket y puerto
	intermediario_address = ('localhost', clientAddress)
	print 'Empezando a levantar %s puerto %s' % intermediario_address
	sockListenClient.bind(intermediario_address)

	# Conecta el socket en el puerto cuando el servidor esté escuchando
	server_address = ('localhost', serverAddress)
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
