#!/usr/bin/python
# -*- coding: utf-8 -*-
 
# Programa Cliente
# Fuente original de este codigo: www.pythondiario.com
# Utilizado para fines academicos en el curso CI-1320 

import socket
import sys

# Variables "Globales"
windowSR = 3
file_Name = 'datos.txt'
intermediate_port = 10000
mode = 'normal'
time_out = 3
sec_Packet = 0
 
# Creando un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Solicitud del tamaño de la ventana de paso de Selective Repeat
windowSR = input("Tamaño deseado de la ventana de paso: ")

# Solicitud y carga de archivo a enviar
file_Name = raw_input("Archivo a ser enviado: ")
file_Open = open(file_Name, 'r')

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
line = file_Open.readline()
while line != "":
	# enviar caracter por caracter.
	leng = len(line)
	for i in xrange(leng):
		sec_Packet = sec_Packet + 1
		packet = (sec_Packet, line[i])
		if mode == "debug":
			if line[i] == " ":
				print "[debug] #%s:_%s" % packet
			else:
				if ord(line[i]) != 10:
					print "[debug] #%s:%s" % packet

	line = file_Open.readline()
print "Archivo enviado."
file_Open.close()

####################################################
#		ELIMINAR
####################################################
 
# Conecta el socket en el puerto cuando el servidor esté escuchando
server_address = ('localhost', intermediate_port)
print >>sys.stderr, 'conectando a %s puerto %s' % server_address
sock.connect(server_address)

try:

    # Enviando datos
    message = 'Este es el mensaje.  Se repitio.'
    print >>sys.stderr, 'enviando "%s"' % message
    sock.sendall(message)
 
    # Buscando respuesta
    amount_received = 0
    amount_expected = len(message)
     
    while amount_received < amount_expected:
        data = sock.recv(19)
        amount_received += len(data)
        print >>sys.stderr, '[debug] ACK %s recibido' % data
 
finally:
    print >>sys.stderr, 'Conexion finalizada'
    sock.close()


