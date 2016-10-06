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

RECV_BUFFER = MTU # Receive buffer size
MEDIUM_STATUS = 'I'


NUM_OF_COLLISION = 0
trans_data = 'DATA'
DURING_TRANSMIT = False

START = None
END = 10

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

    tout = False

    s = connect_to_medium() # Connection

    START = time.time()

    # recv_packet is the function that receiving packets. Transmission and receiving is separated.
    t = Timer(0,recv_packet,[s])
    t.start()

    # Util before timeout or even if timeout, finishing handling collision.
    while time.time()-START < END:

	# Random packet generator. It use gauss distribution. Mean is set by 50, and Standard
	randnum = generate_random()
        if randnum > 54:
		# Before real transmit packet routine, save how many occur sequential collision before
		before_collision = NUM_OF_COLLISION

		# Decide this routine is for handling collsion or new transmit packet.
		if NUM_OF_COLLISION == 0 and handling_collision == False:
                  trans_data = 'DATA' # Data will be stored in packet
	          while MEDIUM_STATUS == 'B':
		    #if time.time()-START > END:
                    #  tout=True
 		    #  break
		    continue
		else: # Collision handling
		  # Set the backoff time slot by picking random number
		  if NUM_OF_COLLISION < 6:
		    slot = random.randint( 0, 2**(NUM_OF_COLLISION+2)-1 )
		  else:
		    slot = random.randint( 0, 2**8-1 )
		  while slot != 0 and tout == False:
		    # Before sleep a slot time, if medium is BUSY, then wait until become IDLE
		    while MEDIUM_STATUS == 'B':
                      #if time.time()-START > END:
                      #  tout=True
                      #  break
		      continue
		    # Sleep a slot time, 1/100 of packet transmission time
		    time.sleep(MTU/(BANDWIDTH*100))
		    slot -= 1

		if tout == True:
		  break

		# Checking Begin Transmit
	        DURING_TRANSMIT = True
                transmit(s,trans_data) # Transmit a data packet

		# Waiting until process receive information that medium is idle. It is required for avoiding self-collision.
	        while DURING_TRANSMIT == True and time.time()-START < END:
                  continue

		# Checking occur collision or not during this transmit.
		# If the transmission occur collision, set handling_collision true.
		# If not, just finish the transmit, if handling_collision is true, then reset the collision status.
		if NUM_OF_COLLISION!=0 and before_collision != NUM_OF_COLLISION:
		  handling_collision = True
		else:
		  if handling_collision == True:
		    NUM_OF_COLLISION = 0
		    handling_collision = False
        else:
	  time.sleep(0.0001)

    # After while routine, set TIMEOUT True and wait until receiving thread is canceled, and then system exit.
    TIMEOUT=True
    t.cancel()
    t.join()
    s.close()
    sys.exit()


# This function receives packets and divides whether a packet is data packet or signal of medium status.
def recv_packet(s):
    global MEDIUM_STATUS
    global RECV_BUFFER
    global NUM_OF_COLLISION
    global trans_data
    global DURING_TRANSMIT
    global START
    global END
    global TIMEOUT

    # loop until timeout. 
    while not TIMEOUT:

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
		 # Sensing the medium status 
                if data[0:6] == '\t:!?:\t':
		  #print 'sign ' + data[6]
		  # Sensing Medium Collision
		  if data[6]=='C':
		      NUM_OF_COLLISION += 1
		  # Sensing Medium become BUSY or IDLE
		  else:
                    MEDIUM_STATUS = data[6]
		    if MEDIUM_STATUS == 'I' and DURING_TRANSMIT==True:
		      DURING_TRANSMIT = False
		# Receive a packet
                else:
                  print("\nReceive a packet : %s" % data)
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

# Generate random number with random.gauss() function. random.gauss() pick a number according to gaussian distribution.
# The first option is mean, and second option is standard deviation. 
def generate_random():
  num = random.gauss(50, 1)
  while num <0 or num >100:
    num = random.gauss(50, 1)
  return num

if __name__ == "__main__":
    sys.exit(node())

