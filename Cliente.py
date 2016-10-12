#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Programa Cliente
# Fuente original de este codigo: www.pythondiario.com
# Utilizado para fines academicos en el curso CI-1320 

import socket
import sys
import os.path
import time

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
iDs = windowSR * 2 - 1 #AGREGUÉ EL -1 PORQUE LOS ID VAN DE 0 a TAMAÑO VENTANA -1

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
 
# Conecta el socket en el puerto cuando el servidor esté escuchando
server_address = ('localhost', intermediate_port)
print >>sys.stderr, 'conectando a %s puerto %s' % server_address
sock.connect(server_address)


# Enviar datos del cliente hacia el servidor
line = file_Open.readline()
act_Id = 0
leng = len(line)
try:
	sock.settimeout(0.1)
	# Llena la ventana inicial
	for i in xrange(windowSR):
		packet = str(act_Id)
		packet += ":"
		packet += line[i]
		
		vecWindow.append(packet)
		vecId.append(act_Id)			
		act_Id += 1
		leng -= 1

		if mode == "debug":
			print "[debug] enviando el paquete: #%s" % vecWindow[-1]

		sock.sendall(vecWindow[-1])
		t_a = time.time()
		t = t_a + time_out
		vecTimer.append(t)

 
 	# Inicia el envio de paquetes cuando se mueva la ventana
 	finish = False

	while not finish:
		noMsn = False
		while not noMsn:
			print "enter"
			try:
				print "enter enter"
				data = sock.recv(5)
				ack = data.split(':')[0]
				ack_Id = int(ack)

				if mode == "debug":
					print >>sys.stderr, '[debug] ACK %s recibido' % ack_Id

				if ack_Id in vecId:
					pos = vecId.index(ack_Id)
					vecId[pos] = -1
			except:
				print "enter no enter"
				noMsn = True

		if leng == 0:
			line = file_Open.readline()
			leng = len(line)

		while vecId and vecId[0] == -1:
			vecWindow.pop(0)
			vecTimer.pop(0)
			vecId.pop(0)

			if 0 < leng:
				act_Ch = len(line) - leng

				packet = str(act_Id)
				packet += ":"
				packet += line[act_Ch]

				vecWindow.append(packet)
				vecTimer.append(t)
				vecId.append(act_Id)
				act_Id += 1
				leng -= 1

				if act_Id > iDs: #ESTO LO REVISA CADA VEZ QUE AUMENTA. SE PONE CERO CUANDO ES MAYOR QUE IDs NADA MÁS.
					act_Id = 0

				if mode == "debug":
					print "[debug] enviando el paquete: #%s" % vecWindow[-1]
				
				sock.sendall(vecWindow[-1]) #AGREGUÉ ESTA LÍNEA. NUNCA ESTABA ENVIANDO, POR ESO SE QUEDABA EN LOS PRIMEROS PAQUETES QUE ENVIABA.
				t_a = time.time()
				t = t_a + time_out			
				vecTimer.append(t)

			if mode == "debug":
				ventana = "ventana: |"
				for i in xrange(len(vecWindow)):
					ventana += vecWindow[i]
					ventana += "|"
				print "[debug] %s" % ventana

		t_a = time.time()
		for act in xrange(len(vecWindow)):
			if t_a >= vecTimer[act]:
				if mode == "debug":
					print "[debug] Reenviando el paquete: #%s" % vecWindow[act]
				sock.sendall(vecWindow[act])
				t_b = time.time()
				t = t_b + time_out
				vecTimer[act] = t

		if not vecWindow:
			finish = True

finally:
	print >>sys.stderr, 'Conexion finalizada'
	sock.close()
