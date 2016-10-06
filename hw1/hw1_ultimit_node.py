import sys
import socket
import select
import time
import random
from threading import Timer


# Settable parameters
BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
MTU = 1000 # Maximum Transmit Unit for this medium (B)
PDELAY = 0.1 # Propagation delay (s)

RECV_BUFFER = 2*MTU # Receive buffer size
MEDIUM_STATUS = 'I'


NUM_OF_COLLISION = 0
trans_data = 'DATA'
DURING_TRANSMIT = False

START = None
END = 30

TIMEOUT = False

def node():

    global MEDIUM_STATUS
    global NUM_OF_COLLISION
    global DURING_TRANSMIT
    global trans_data
    global START
    global END
    global TIMEOUT

    t = None
    handling_collision = False
    before_collision = 0

    s = connect_to_medium() # Connection

    START = time.time()

    t = Timer(1,recv_packet,[s])
    t.start()

    while time.time()-START < END or handling_collision:
	randnum = generate_random()
        if randnum > 53.2:
		#print randnum
		before_collision = NUM_OF_COLLISION

		if NUM_OF_COLLISION == 0 and handling_collision == False:
                  trans_data = 'DATA' # Data will be stored in packet
	          #while MEDIUM_STATUS == 'B' and time.time()-START < END:
	          while MEDIUM_STATUS == 'B':
		    continue
		else: #Collision handling
		  #print('==Collision handling Procedure - COLLISION '+str(NUM_OF_COLLISION)+'==')
		  slot = random.randint( 0, 2**(NUM_OF_COLLISION+2)-1 )
		  #print('set backoff time slot: '+str(slot))
		  while slot != 0:
		    #print(slot)
		    #while MEDIUM_STATUS == 'B' and time.time()-START < END:
		    while MEDIUM_STATUS == 'B':
		      continue
		    time.sleep(MTU/(BANDWIDTH*100))
		    slot -= 1

	        DURING_TRANSMIT = True
                transmit(s,trans_data) # Transmit a data packet

	        #while DURING_TRANSMIT == True and time.time()-START < END:
	        while DURING_TRANSMIT == True:
                  continue

		if NUM_OF_COLLISION!=0 and before_collision != NUM_OF_COLLISION:
		  #print('@@@@@Sensing the Collision'+str(NUM_OF_COLLISION)+'th@@@@@@@')
		  handling_collision = True
		elif MEDIUM_STATUS == 'I':
		  #print('END with \'I\'')
		  if handling_collision == True:
		    #print '~~AND~~ It handling collision!!'
		    NUM_OF_COLLISION = 0
		    handling_collision = False
	          #trans_data = ''
		elif MEDIUM_STATUS == 'B':
		  #print('***WHAT HAPPEN?! STATUS IS \'B\', BUT IT IS TRANSMITED WELL?!')
		  if handling_collision == True:
		    #print('*#*#Also, It is collision situation?!?!#*#*')
                    NUM_OF_COLLISION = 0
                    handling_collision = False
                  #trans_data = 

    TIMEOUT=True
    t.cancel()
    t.join()
    s.close()
    sys.exit()


def recv_packet(s):
    global MEDIUM_STATUS
    global RECV_BUFFER
    global NUM_OF_COLLISION
    global trans_data
    global DURING_TRANSMIT
    global START
    global END
    global TIMEOUT


    while not TIMEOUT:
	flag = True
        socket_list = [s]

        # Get the list sockets which are readable
	ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [], 0)

        for sock in ready_to_read:
              # Incoming data packet from medium
              packet = sock.recv(RECV_BUFFER) # Recive a packet
              data = extract_data(packet) # Extract data in a packet
              if not data:
                print('\nDisconnected')
                sys.exit()
              else:
                if data[0:6] == '\t:!?:\t':
		  if data[6]=='C':
		    #if DURING_TRANSMIT==True:
		    #print('Recv Collision!')
		    if NUM_OF_COLLISION <= 5:
		      NUM_OF_COLLISION += 1
		      #DURING_TRANSMIT = False
		  else:
                    MEDIUM_STATUS = data[6]
                    #print('Status changed: '+MEDIUM_STATUS)
		    if MEDIUM_STATUS == 'I' and DURING_TRANSMIT==True:
		      DURING_TRANSMIT = False

                else:
                  #print("\nReceive a packet : %s" % data)

    sys.exit()


# Connect a node to medium ----- recommand not to modify
def connect_to_medium():
  host = '127.0.0.1' # Local host address
  port = 9009 # Medium port number
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  s.settimeout(2)
  try:
    s.connect((host, port))
  except:
    print('Unable to connect')
    sys.exit()

  print('Connected. You can start sending packets')

  return s


# Make and transmit a data packet
def transmit (s, trans_data):
  global PDELAY

  packet = trans_data 

  if len(packet) > MTU:
    print('Cannot transmit a packet -----> packet size exceeds MTU')
  else:
    packet = packet + '0'*(MTU-(len(trans_data)))
    s.send(packet)
    time.sleep(PDELAY)
    #print('Transmit a packet')

# Extract data
def extract_data(packet):
  i=0
  for c in packet:
    if c == '0':
      break
    else:
      i=i+1
      continue

  data = packet[0:i]
  #print 'extract_data: '+data
  return data

def generate_random():
  num = random.gauss(50, 1)
  while num <0 or num >100:
    num = random.gauss(50, 1)

  return num

if __name__ == "__main__":
    sys.exit(node())

