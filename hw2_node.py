import sys
import socket
import select
import time
from threading import Timer


# Settable parameters
BANDWIDTH = 100000 # 1000 = 1KB, in turn, 10000  = 10KB (B/SEC)
MTU = 1000 # Maximum Transmit Unit for this medium (B)
RECV_BUFFER = 2*MTU # Receive buffer size

def node():

    s = connect_to_medium() # Connection
    sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program : '); sys.stdout.flush()

    while 1:
        socket_list = [sys.stdin, s]

        # Get the list sockets which are readable
        ready_to_read, ready_to_write, in_error = select.select(socket_list, [], [])

        for sock in ready_to_read:
            if sock == s:
              # Incoming data packet from medium
              packet = sock.recv(RECV_BUFFER) # Recive a packet
              data = extract_data(packet) # Extract data in a packet
              if not data:
                print('\nDisconnected')
                sys.exit()
              else:
                print("\nReceive a packet : %s" % data)
                sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()
            else:
              cmd = sys.stdin.readline()
              if cmd == 'quit\n':
                s.close()
                sys.exit()
              trans_data = 'DATA' # Data will be stored in packet
              transmit(s,trans_data) # Transmit a data packet
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

  packet = trans_data 

  if len(packet) > MTU:
    print('Cannot transmit a packet -----> packet size exceeds MTU')
  else:
    packet = packet + '0'*(MTU-(len(trans_data)))
    s.send(packet)
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

if __name__ == "__main__":
    sys.exit(node())

