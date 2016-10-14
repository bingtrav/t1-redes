#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Programa Cliente
# Fuente original de este codigo: www.pythondiario.com
# Utilizado para fines academicos en el curso CI-1320 

import socket
import sys
import os.path
import time
from datetime import datetime

# Variables de estadistica
packets = 0
lostPackets = 0
noLostPackets = 0
startTime = time.time()
startClock = datetime.now().strftime('%H:%M:%S')
endTime = 0
endClock = 0
totalTime = 0
# Variables "Globales"
windowSR = 3		# Tamaño de la ventana de Selective Repeat
iDs = 0;			# Cantidad necesaria de IDs unicos
file_Name = 'datos.txt'		# Nombre del archivo a enviar
intermediate_port = 10000	# Puerto de conexión con el intermediario
mode = 'normal'		# Modo de ejecución
time_out = 3		# Tiempo del time-out
sec_Packet = 0		# Secuencia del paquete
vecId = []			# Vector de IDs de los paquetes enviados
vecWindow = []		# Vector de los paquetes enviados
vecTimer = []		# Vector del timer de cada paquete (unico)
vecReSend = []		# Vector de conocimiento de reenvio
 
# Creando un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if len(sys.argv) < 6:
	# Solicitud del tamaño de la ventana de paso de Selective Repeat
	windowSR = int(input("Tamaño deseado de la ventana de paso: "))
	iDs = windowSR * 2

	# Solicitud y carga de archivo a enviar
	is_File = False
	while not is_File:
		file_Name = raw_input("Ingrese archivo a ser enviado: ")
		is_File = os.path.isfile(file_Name)
		if is_File:
			file_Open = open(file_Name, 'r')
		else :
			print "Archivo no encontrado"

	# Solicitar al usuario cual será el puerto de conexión con el intermediario
	is_Port = False
	while not is_Port:
		intermediate_port = input("Puerto de conexión con el intermediario: ")
		# Conecta el socket en el puerto cuando el servidor esté escuchando
		try:
			server_address = ('localhost', intermediate_port)
			sock.connect(server_address)
			print >>sys.stderr, 'Conectando a %s puerto %s' % server_address
			is_Port = True
		except:
			print "Puerto de conexión inválido. Intente de nuevo."

	# Invita al usuario a seleccionar el modo que desee
	mode = raw_input("Ingrese el modo a ejecutar \n normal o debug: ")
	if mode == "normal" or mode == "n":
		mode = "normal"
	else:
		if mode == "debug" or mode == "d":
			mode = "debug"
		else:
			print >>sys.stderr, 'Modo auto-asignado'
			mode = "normal"
	print >>sys.stderr, 'Modo seleccionado: %s' % mode

	# Pide el tiempo de time-out en ms
	time_out = input("Cuanto tiempo desea el Time-Out del ACK: ")
	print >>sys.stderr, 'Tiempo del Time-Out configurado a %i ms' % time_out
	time_out = time_out * 0.001
else:	
	print "Ejecución con parametros"
	windowSR = int(sys.argv[2])
	iDs = windowSR * 2
	intermediate_port = int(sys.argv[1])
	try:
		server_address = ('localhost', intermediate_port)
		sock.connect(server_address)
		print >>sys.stderr, 'Conectando a %s puerto %s' % server_address
		is_Port = True
	except:
		print "Puerto de conexión inválido."
		sys.exit(0)
	is_File = os.path.isfile(sys.argv[3])
	if is_File:
		file_Open = open(sys.argv[3], 'r')
	else:
		print "Archivo no encontrado"
		sys.exit(0)
	mode = sys.argv[4]
	if mode == "d": mode = "debug"
	else: mode = "normal"
	time_out = int(sys.argv[5])
	time_out = time_out * 0.001
 
# Enviar datos del cliente hacia el servidor
line = file_Open.readline()
act_Id = 0
leng = len(line)
try:
	sock.settimeout(0.05)			# Se asigna un tiempo de espera de mensajes limitado 
	# Llena la ventana inicial
	for i in xrange(windowSR):
		packets += 1
		packet = "#"
		packet += str(act_Id)
		packet += ":"
		packet += line[i]
		
		vecWindow.append(packet)
		vecId.append(act_Id)
		vecReSend.append(False)
		act_Id += 1
		leng -= 1

		if mode == "debug":
			print "[debug] enviando el paquete: %s" % vecWindow[-1]
		sock.sendall(vecWindow[-1])
		t_a = time.time()
		t = t_a + time_out
		vecTimer.append(t)
 
 	# Inicia el envio de paquetes cuando se mueva la ventana
 	finish = False

	while not finish:
		# Revisa todos los ACKs recibidos.
		noMsn = False
		while not noMsn:
			try:
				data = sock.recv(1000)
				vecAck = data.split('#')
				vecAck.pop(0)
				for ac in vecAck:
					ack = ac.split(':')[0]
					ack_Id = int(ack)

					if mode == "debug":
						print >>sys.stderr, '[debug] ACK %s recibido' % ack_Id

					if ack_Id in vecId:
						pos = vecId.index(ack_Id)
						vecId[pos] = -1
			except:
				noMsn = True

		# Si ya no hay más en la linea, saca la siguiente.
		finDoc = False			
		if leng == 0:
			line = file_Open.readline()
			leng = len(line)
			if leng == 0:
				finDoc = True

		# Revisa que la ventana contenga algo y luego si el primer paquete fue recibido para moverla y enviar otro.
		while vecId and vecId[0] == -1:
			if not finDoc and 0 < leng:
				if not vecReSend[0]:
					noLostPackets += 1

				vecWindow.pop(0)
				vecTimer.pop(0)
				vecId.pop(0)
				vecReSend.pop(0)

				act_Ch = len(line) - leng

				packets += 1
				packet = "#"
				packet += str(act_Id)
				packet += ":"
				packet += line[act_Ch]

				vecWindow.append(packet)
				vecTimer.append(t)
				vecId.append(act_Id)
				vecReSend.append(False)
				act_Id += 1
				leng -= 1

				if act_Id > iDs:
					act_Id = 0

				if mode == "debug":
					print "[debug] enviando el paquete: %s" % vecWindow[-1]
				sock.sendall(vecWindow[-1])
				t_a = time.time()
				t = t_a + time_out			
				vecTimer.append(t)
			else:
				if finDoc:
					vecWindow.pop(0)
					vecTimer.pop(0)
					vecId.pop(0)
					vecReSend.pop(0)
				break

			# if mode == "debug" and vecId:
			# 	ventana = "ventana: |"
			# 	for i in xrange(len(vecWindow)):
			# 		ventana += vecWindow[i]
			# 		ventana += "|"
			# 	print "[debug] %s" % ventana

		# Revisa cada paquete si hay time-out como si se revisaran todos al mismo tiempo.
		t_a = time.time()
		for act in xrange(len(vecWindow)):
			if t_a >= vecTimer[act]:
				if mode == "debug":
					print "[debug] Reenviando el paquete: %s" % vecWindow[act]
				sock.sendall(vecWindow[act])
				vecReSend[act] = True
				t_b = time.time()
				t = t_b + time_out
				vecTimer[act] = t

		# Si ya no hay nada en la ventana significa que ya no hay paquetes que enviar ni reenviar.
		if not vecWindow:
			endTime = time.time()
			endClock = datetime.now().strftime('%H:%M:%S')
			totalTime = endTime - startTime
			lostPackets = packets - noLostPackets
			finish = True

finally:
	print >>sys.stderr, 'Conexion finalizada'
	sock.close()

print "ESTADISTICA"
print "Hora inicio: %s" %startClock
print "Hora final: %s" %endClock
print "Duracion: %s" %totalTime
print "Paquetes no perdidos: %s" %noLostPackets
print "Paquetes perdidos: %s" %lostPackets