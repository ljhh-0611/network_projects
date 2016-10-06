import sys
import socket
import select
import time
import random
from threading import Timer


# Settable parameters
BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
MTU = 1000 # Maximum Transmit Unit for this medium (B)
PDELAY = 0.5 # Propagation delay (s)

RECV_BUFFER = 2*MTU # Receive buffer size
MEDIUM_STATUS = 'I'


NUM_OF_COLLISION = 0
trans_data = ''
DURING_TRANSMIT = False

def node():

    global MEDIUM_STATUS
    global NUM_OF_COLLISION
    global DURING_TRANSMIT
    global trans_data

    t = None
    handling_collision = False
    before_collision = None
    #trans_data = ''

    s = connect_to_medium() # Connection
    t = Timer(1,recv_packet,[s])
    t.start()

    while 1:
	randnum = generate_random()
        if randnum >= 49:
		before_collision = NUM_OF_COLLISION
                #if cmd == 'quit\n':
		  #t.cancel()
                 # s.close()
		 # t.cancel()
                 # sys.exit()

		if NUM_OF_COLLISION == 0 and handling_collision == False:############################################################################NUM_OF_COLLISION == 0:
                  trans_data = 'DATA' # Data will be stored in packet
	          while MEDIUM_STATUS == 'B':
		    continue
		else: #Collision handling
		  print('==Collision handling Procedure==')
		  ###########################################################################################handling_collision = True
		  slot = random.randint( 0, 2**(NUM_OF_COLLISION+2)-1 )
		  print('set backoff time slot: '+str(slot))
		  while slot != 0:
		    print(slot)
		    while MEDIUM_STATUS == 'B':
		      continue
		    time.sleep(MTU/(BANDWIDTH*100))
		    slot -= 1
		  #FIXME first, set backoff time. Second, each backoff slot, look whether the MEDIUM_STATUS is I or B. ... If B, then wait until become I. Then sleep a backoff time.

	        DURING_TRANSMIT = True
                transmit(s,trans_data) # Transmit a data packet

	        while  DURING_TRANSMIT == True:
                  continue

		if MEDIUM_STATUS == 'I':
		  #print('transmit complete normally')
		  if NUM_OF_COLLISION > 0 and handling_collision == True:
		    NUM_OF_COLLISION = 0
		    handling_collision = False
	          trans_data = ''
		elif NUM_OF_COLLISION!=0 and before_collision != NUM_OF_COLLISION:
		  print('@@@@@Sensing the Collision'+str(NUM_OF_COLLISION)+'th@@@@@@@')
		  handling_collision = True
		elif MEDIUM_STATUS == 'B':
		  print('***WHAT HAPPEN?! STATUS IS \'B\', BUT IT IS TRANSMITED WELL?!')
		  if NUM_OF_COLLISION > 0 and handling_collision == True:
		    print('*#*#Also, It is collision situation?!?!#*#*')
                    NUM_OF_COLLISION = 0
                    handling_collision = False
                  trans_data = ''
	        #cur_msg = trans_data

  		#FIXME Change with current thread and main thread

def recv_packet(s):
    global MEDIUM_STATUS
    global RECV_BUFFER
    global NUM_OF_COLLISION
    global trans_data
    global DURING_TRANSMIT

    while 1:
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
                if data[0:6]== '\t:!?:\t':
		  if data[6]=='C' and trans_data != '':
		    print('Recv Collision!')
		    if NUM_OF_COLLISION <= 5:
		      NUM_OF_COLLISION += 1
		    DURING_TRANSMIT = False
		  else:
                    MEDIUM_STATUS = data[6]
                    print('Status changed: '+MEDIUM_STATUS)
		    if MEDIUM_STATUS == 'I':
		      DURING_TRANSMIT = False
                else:
                  print("\nReceive a packet : %s" % data)
                  sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()


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
    print('Transmit a packet')

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
  return data

def generate_random():
  sys.stdout.write('@'); sys.stdout.flush()
  num = random.gauss(50, 1)
  while num <0 or num >100:
    num = random.gauss(50, 1)

  return num

if __name__ == "__main__":
    sys.exit(node())

