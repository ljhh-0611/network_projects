import sys
import socket
import select
import time
import random
from threading import Timer

NODE_LIST = []
NODE_NUM_LIST = []

# Settable parameters
NUM_OF_NODES = 10 # The maximum number of nodes
BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
MTU = 1000 # Maximum Transmit Unit for this medium (B)
RECV_BUFFER = MTU # Receive buffer size
PDELAY = 0.1 # Propagation delay (s)

IDLE = 'I'
BUSY = 'B'

#Global variable
STATUS = IDLE # Status of Medium : I -> Idle, B -> Busy

MEDIUM_COST = 9999

def medium():

    global STATUS # Status of Medium : I -> Idle, B -> Busy
    global MEDIUM_COST
    global NODE_LIST
    global NODE_NUM_LIST

    t=None # Event Scheduler
    num_of_connected_nodes = 0

    #MEDIUM_COST = raw_input('Put the cost of This Medium: ')
    #while not MEDIUM_COST.isdigit():
    #  MEDIUM_COST = raw_input('It is NOT DIGIT. plz Put again: ')

    MEDIUM_COST = random.randrange(1,20)
    print ('This MEDIUM costs '+str(MEDIUM_COST))

    NODE_LIST.append(sys.stdin)
    sys.stdout.write('Put the Node Number to Connect: '); sys.stdout.flush()

    while 1:
      try:
        # Get the list sockets which are ready to be read through select
        ready_to_read, ready_to_write, in_error = select.select(NODE_LIST, [], [], 0)

        for sock in ready_to_read:
            try:
              if sock == sys.stdin:
                cmd = sys.stdin.readline().rstrip('\n')
                if cmd == 'quit':
                 # s.close()
                  sys.exit()
                if num_of_connected_nodes < 2:
		  if not cmd.isdigit():
		    print('Wrong! It is not digit!')
		    sys.stdout.write('Put the Node Number to Connect: '); sys.stdout.flush()
		    continue
                  node_num = int(cmd)
                  nodes = connect_to_router(node_num)
		  NODE_LIST.append(nodes)
		  NODE_NUM_LIST.append(node_num)
                  num_of_connected_nodes += 1

                  if num_of_connected_nodes == 1:
    		    sys.stdout.write('Put the Node Number to Connect: '); sys.stdout.flush()
		  elif num_of_connected_nodes == 2:
		    print('Two Nodes are Connected!')
		    change_status()
		    forward_connect()

		else:
		  print('Already Two Nodes are Connected!')
                #sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()
                # Receiving packet from the socket.

	      else:
                packet = sock.recv(RECV_BUFFER)

                if packet:
                  # Check medium here!
                  """if STATUS == BUSY:
                    print('Collision has happend on medium!')
                    t.cancel()
                    Timer(MTU/BANDWIDTH,change_status).start() # Collided packet is still in medium
                  # Collision occurs!
                  elif STATUS ==IDLE:
                    change_status() #Change status to busy
                    # Message packet is being propagated to nodes through medium
                    t=Timer(MTU/BANDWIDTH,forward_pkt, (sys.stdin, sock, packet))
                    t.start()
                  else:
                    print('Undefined status')"""
		  forward_pkt(sys.stdin,sock,packet)
                else:
                  if node in NODE_LIST:
                    print("Node (%s, %s) disconnected" % node.getpeername())
                    NODE_LIST.remove(node)
                    continue

            # Exception
            except:
              if node in NODE_LIST:
                print("Error! Check Node (%s, %s)" % node.getpeername())
                SOCKET_LIST.remove(node)
              continue
      except:
        sys.exit()


# Connect a node to medium ----- recommand not to modify
def connect_to_router(node_num):
  host = '127.0.0.1' # Local host address
  port = node_num # Medium port number
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  s.settimeout(2)
  try:
    s.connect((host, port))
  except:
    print('Unable to connect')
    sys.exit()

  print('Connected. You will receive data of Node'+str(node_num))

  return s


# Forward_pkt to all connected nodes exclude itself(source node)
def forward_pkt (medium_socket, sock, message):
 
    global STATUS
    global NODE_LIST

    for socket in NODE_LIST:
        # Send the message only to peer
        if socket != medium_socket and socket != sock:
            try:
                socket.send(message)
            except:
                # Broken socket connection
                socket.close()
                # Broken socket, remove it
                if socket in NODE_LIST:
                    NODE_LIST.remove(socket)

    #Packet transmission is finished

    #change_status() #Change status to idle

def forward_connect ():

  global STATUS
  global MEDIUM_COST

  for socket in NODE_LIST:
    # Send the message only to peer
    if socket != sys.stdin:
        try:
     	    if socket == NODE_LIST[1]:
	      message = 'Connected'+str( {NODE_NUM_LIST[1]:MEDIUM_COST} )
  	      packet = message + '*'*(MTU-(len(message)))
              socket.send(packet)
     	    elif socket == NODE_LIST[2]:
	      message = 'Connected'+str( {NODE_NUM_LIST[0]:MEDIUM_COST} )
  	      packet = message + '*'*(MTU-(len(message)))
              socket.send(packet)
        except:
	    print('=======socket broken===========')
            # Broken socket connection
            socket.close()
            # Broken socket, remove it
            if socket in NODE_LIST:
              NODE_LIST.remove(socket)
  print('Transmit the connect information')
  change_status()

# Chaning medium status 
def change_status():

    global STATUS

    if STATUS == 'B':
       STATUS = 'I'
    elif STATUS == 'I':
       STATUS = 'B'

if __name__ == "__main__":
    sys.exit(medium())
