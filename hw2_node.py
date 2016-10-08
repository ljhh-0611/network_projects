import sys
import socket
import select
import time
import ast
from threading import Timer

HOST = ''

# Settable parameters
MAX_EDGES = 10
BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
MTU = 1000 # Maximum Transmit Unit for this medium (B)
RECV_BUFFER = MTU # Receive buffer size

MEDIUM_LIST = []
NODE_NUM = None
ADJACENT_NODES = {}

node_socket = None

def node():

    global node_socket

    NODE_NUM = raw_input("input Node Number (9100~): ")

    while not NODE_NUM.isdigit() or ( NODE_NUM.isdigit() and NODE_NUM < 9100 ):
	print('Wrong! input again')
        NODE_NUM = input("input Node Number (9100~): ")

    NODE_NUM = int(NODE_NUM)
    node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    node_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    node_socket.bind((HOST, NODE_NUM))
    node_socket.listen(MAX_EDGES)

    MEDIUM_LIST.append(node_socket)

    print("Node is Created (Number:" + str(NODE_NUM) + ") ")

    MEDIUM_LIST.append(sys.stdin)

    while 1:
        try:
            # Get the list sockets which are readable
            ready_to_read, ready_to_write, in_error = select.select(MEDIUM_LIST, [], [])

            for sock in ready_to_read:
		if sock == node_socket: # 0.0.0.0 : 9009 (sock)
            	  sockfd, addr = node_socket.accept()
            	  MEDIUM_LIST.append(sockfd)
            	  print("Medium (%s, %s) connected" % addr)
                elif sock == sys.stdin:
                  cmd = sys.stdin.readline()
                  if cmd == 'quit\n':
                    #s.close()
                    sys.exit()
                  #trans_data = 'DATA' # Data will be stored in packet
                  transmit() # Transmit a data packet
                  #sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()
                  sys.stdout.write('YOU Press ENTER key\n'); sys.stdout.flush()
                else:
                # Incoming data packet from medium
                  packet = sock.recv(RECV_BUFFER) # Recive a packet
                  data = extract_data(packet) # Extract data in a packet

		  if data[0:9] == 'Connected':
		    print data[9:]
		    print 'data[9:] type is ' + str(type(data[9:]))
		    new_dict = ast.literal_eval(data[9:])
		    print new_dict
                    print 'new_dict type is ' + str(type(new_dict))
		    ADJACENT_NODES.update(new_dict)
		    print ADJACENT_NODES
                  elif not data:
                    print('\nNot data?!')
                    print('\nDisconnected')
                    sys.exit()
                  else:
                    print("\nReceive a packet : %s" % data)
                    #sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()
                    #sys.stdout.write('YOU receive something'); sys.stdout.flush()
        except:
            print('\nNode program is terminated')
            node_socket.close()
            sys.exit()


# Make and transmit a data packet
def transmit ():

  global node_socket

  if len(str(ADJACENT_NODES)) > MTU:
    print('Cannot transmit a packet -----> packet size exceeds MTU')
  else:
    packet = str(ADJACENT_NODES) + '*'*(MTU-(len(str(ADJACENT_NODES))))
    for socket in MEDIUM_LIST:
      if socket != sys.stdin and socket != node_socket:
    	socket.send(packet)
    print('Transmit a packet')

# Extract data
def extract_data(packet):
  i=0
  for c in packet:
    if c == '*':
      break
    else:
      i=i+1
      continue

  data = packet[0:i]
  print data
  return data

if __name__ == "__main__":
    sys.exit(node())

