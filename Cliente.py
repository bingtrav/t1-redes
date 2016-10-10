#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Programa Cliente
# Fuente original de este codigo: www.pythondiario.com
# Utilizado para fines academicos en el curso CI-1320 

import socket
import sys
import os.path

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
 
# Creando un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Solicitud del tamaño de la ventana de paso de Selective Repeat
windowSR = input("Tamaño deseado de la ventana de paso: ")
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
intermediate_port = input("Puerto de conexión con el intermediario: ")

# Invita al usuario a seleccionar el modo que desee
mode = raw_input("Ingrese el modo a ejecutar \n normal o debug: ")
print >>sys.stderr, 'Modo seleccionado: %s' % mode

# Pide el tiempo de time-out en ms
time_out = input("Cuanto tiempo desea el Time-Out del ACK: ")
print >>sys.stderr, 'Tiempo del Time-Out configurado a %i ms' % time_out

####################################################
#		ELIMINAR
####################################################

# Enviar datos del cliente hacia el servidor
# line = file_Open.readline()
# act_Id = 0
# while line != "":
# 	# enviar caracter por caracter.
# 	leng = len(line)
# 	for i in xrange(leng):
# 		sec_Packet = sec_Packet + 1
# 		packet = (sec_Packet, line[i])
# 		if mode == "debug":
# 			if line[i] == " ":
# 				vecWindow.append(packet)
# 				vecTimer.append(time_out)
# 				vecId.append(act_Id)
# 				act_Id += 1
# 				print "[debug] #%s:_%s" % packet
# 				print "[debug] esperando en ventana el paquete: #%s:_%s"  % vecWindow[-1]
# 			else:
# 				if ord(line[i]) != 10:
# 					vecWindow.append(packet)
# 					vecTimer.append(time_out)
# 					vecId.append(act_Id)
# 					act_Id += 1
# 					print "[debug] %s:%s" % packet
# 					print "[debug] esperando en ventana el paquete: #%s:%s" % vecWindow[-1]
# 		if act_Id == iDs
# 			act_Id = 0
# 	line = file_Open.readline()
# print "Archivo enviado."
# file_Open.close()

####################################################
#		ELIMINAR
####################################################
 
# Conecta el socket en el puerto cuando el servidor esté escuchando
server_address = ('localhost', intermediate_port)
print >>sys.stderr, 'conectando a %s puerto %s' % server_address
sock.connect(server_address)


# Enviar datos del cliente hacia el servidor
line = file_Open.readline()
act_Id = 0
leng = len(line)
try:

	# Llena la ventana inicial
	for i in xrange(windowSR):
		packet = str(act_Id)
		packet += ":"
		packet += line[i]
		
		vecWindow.append(packet)
		vecTimer.append(time_out)
		vecId.append(act_Id)			
		act_Id += 1
		leng -= 1

		if mode == "debug" || mode == "d":
			print "[debug] enviando el paquete: #%s" % vecWindow[-1]

		sock.sendall(vecWindow[-1])

 
 	# Inicia el envio de paquetes cuando se mueva la ventana
 	finish = False

	while not finish:
		data = sock.recv(5)
		ack = data.split(':')[0]
		ack_Id = int(ack)

		vecId[ack_Id] = -1
		neutral = vecId[ack_Id]

		while vecId[0] == -1 and 0 < leng:
			print "entra %s" % vecId[0]
			vecWindow.pop(0)
			vecTimer.pop(0)
			vecId.pop(0)

			act_Ch = len(line) - leng

			packet = str(act_Id)
			packet += ":"
			packet += line[act_Ch]

			vecWindow.append(packet)
			vecTimer.append(time_out)
			vecId.append(act_Id)
			act_Id += 1
			leng -= 1

			if mode == "debug" || mode == "d":
				print "[debug] enviando el paquete: #%s" % vecWindow[-1]

			for x in xrange(len(vecId)):
				nu = (x,vecWindow[x])
				print "%s:%s" % nu

		if mode == "debug" || mode == "d":
			print >>sys.stderr, '[debug] ACK %s recibido' % ack

		if leng == 0:
			line = file_Open.readline()
			leng = len(line)

		if act_Id == iDs:
			act_Id = 0

		if line == "":
			finish = True

finally:
	print >>sys.stderr, 'Conexion finalizada'
	sock.close()
