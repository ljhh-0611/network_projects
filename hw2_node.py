from __future__ import generators
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

#For Communication with Adjacent Nodes
MEDIUM_LIST = []
NODE_NUM = 0
ADJACENT_NODES = {}
NODE_CONNECTION = {}

node_socket = None

# For Reliable Flooding Phase
FLOODING = False
MAP = {}
ADJACENT_INFORMATION = {}
TO_RECEIVE_INFORMATION = []

MAKING_MAP = False


def node():

    global node_socket
    global FLOODING
    global MAP
    global NODE_NUM
    global MAKING_MAP

    NODE_NUM = raw_input("input Node Number (9100~): ")

    while not NODE_NUM.isdigit() or ( NODE_NUM.isdigit() and NODE_NUM < 9100 ):
	print('Wrong! input again')
        NODE_NUM = raw_input("input Node Number (9100~): ")

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
                  cmd = sys.stdin.readline().rstrip('\n')
                  if cmd == 'quit':
                    #s.close()
                    sys.exit()
		  elif cmd == 'start':
		    if FLOODING == False:
		      FLOODING = True
		      MAP[NODE_NUM] = ADJACENT_NODES
		    forward_map_information()
		  elif cmd == 'dijk':
		    for nodes in MAP:
		      if nodes != NODE_NUM:
		        dijkstra(NODE_NUM, nodes)
		  else:
                    #trans_data = 'DATA' # Data will be stored in packet
                    transmit() # Transmit a data packet
                    #sys.stdout.write('Press ENTER key for transmitting a packet or type \'quit\' to end this program. : '); sys.stdout.flush()
                    sys.stdout.write('YOU Press ENTER key\n'); sys.stdout.flush()
                else:
                # Incoming data packet from medium
                  packet = sock.recv(RECV_BUFFER) # Recive a packet
                  data = extract_data(packet) # Extract data in a packet
		  if data[0:9] == 'Connected':
		    new_dict = ast.literal_eval(data[9:])
		    ADJACENT_NODES.update(new_dict)
		    print ADJACENT_NODES
		    NODE_CONNECTION[ int(data[9:].split(':')[0][1:]) ] = sock
		    print NODE_CONNECTION
		  elif data[0:9] == 'FLOODING_':
                    if FLOODING == False:
                      FLOODING = True
                      MAP[NODE_NUM] = ADJACENT_NODES
		    flood_node_num = int( data[9:].split('_')[0] )
		    flood_node_map = ast.literal_eval( data[9:].split('_')[1] )
		    update_map( flood_node_num,flood_node_map )
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

def forward_map_information ():

  global NODE_NUM
  global MTU
  global MEDIUM_LIST

  global FLOODING
  global MAP
  global ADJACENT_INFORMATION
  global TO_RECEIVE_INFORMATION
  global ADJACENT_NODES
  global NODE_CONNECTION

  map_keys = list(MAP.keys())
  num_of_sending = 0

  message = 'FLOODING_'+str(NODE_NUM)+'_'+str(MAP)
  packet = message + '*'*(MTU-(len(message)))
  for node in ADJACENT_NODES:
      #Case of forward information. First, I don't have any information of the node. Second, the node doesn't have some information that this node has.
    if not node in map_keys or list( set(map_keys) - set(ADJACENT_INFORMATION.get(node).keys()) ):
      try:
        NODE_CONNECTION.get(node).send(packet)
	num_of_sending += 1
        if node in ADJACENT_INFORMATION:
	  del ADJACENT_INFORMATION[node]
	ADJACENT_INFORMATION[node] = MAP
      except:
          print('=======node_medium broken===========')
          # Broken socket connection
          NODE_CONNECTION.get(node).close()
          # Broken socket, remove it
          if NODE_CONNECTION.get(node) in MEDIUM_LIST:
            MEDIUM_LIST.remove( NODE_CONNECTION.get(node) )
	    del NODE_CONNECTION[node]
	    del ADJACENT_NODES[node]

  if num_of_sending == 0 and TO_RECEIVE_INFORMATION == []:
    FLOODING = False
 

def update_map (flood_node_num,flood_node_map) :

  global MAP
  global ADJACENT_INFORMATION
  global TO_RECEIVE_INFORMATION

  reaction_flag = False
  map_keys = list(MAP.keys())

  # update adjacent_information.
  #If flood node's information already exists, then delete old thing and update new thing
  if flood_node_num in map_keys:
    del ADJACENT_INFORMATION[flood_node_num]
  ADJACENT_INFORMATION[flood_node_num] = flood_node_map

  print 'adj_inform: '+str(ADJACENT_INFORMATION)#FIXME
  
  for node_num, adjacent_nodes in flood_node_map.items(): #node_num = a node, adjacent_nodes = nodes_inform of the node
    if not node_num in MAP:
      MAP[node_num] = adjacent_nodes
      if node_num in TO_RECEIVE_INFORMATION:
	TO_RECEIVE_INFORMATION.remove(node_num)

  # Searching some nodes that this node doesn't have in map. If some nodes exist, then ADD them in TO_RECEIVE_INFORMATION
    for anode in adjacent_nodes.keys():
      if not anode in map_keys:
	TO_RECEIVE_INFORMATION.append(anode)

  #print flood_node_map
  print 'MAP: '+str(MAP)#FIXME
  forward_map_information()

def dijkstra(src,dest,visited=[],distances={},predecessors={}):
    global MAP
    # a few sanity checks
    if src not in MAP:
        raise TypeError('the root of the shortest path tree cannot be found in the graph')
    if dest not in MAP:
        raise TypeError('the target of the shortest path cannot be found in the graph')    
    # ending condition
    if src == dest:
        # We build the shortest path and display it
        path=[]
        pred=dest
        while pred != None:
            path.append(pred)
            pred=predecessors.get(pred,None)
	path.reverse()
        print('shortest path: '+str(path)+" cost="+str(distances[dest])) 
    else :	
        # if it is the initial  run, initializes the cost
        if not visited: 
            distances[src]=0
        # visit the neighbors
        for neighbor in MAP[src] :
            if neighbor not in visited:
                new_distance = distances[src] + MAP[src][neighbor]
                if new_distance < distances.get(neighbor,float('inf')):
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = src
        # mark as visited
        visited.append(src)
        # now that all neighbors have been visited: recurse                         
        # select the non visited node with lowest distance 'x'
        # run Dijskstra with src='x'
        unvisited={}
        for k in MAP:
            if k not in visited:
                unvisited[k] = distances.get(k,float('inf')) 
        x=min(unvisited, key=unvisited.get)
        dijkstra(x,dest,visited,distances,predecessors)


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
  return data



if __name__ == "__main__":
    sys.exit(node())

