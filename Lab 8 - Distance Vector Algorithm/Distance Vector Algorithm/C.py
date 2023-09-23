from collections import defaultdict
import heapq as heap
import math
import socket
import os
import socket
import threading
import time
import random


curr='C'
ipport={"A":(9771),"B":(9772),"C":(9773),"D":(9774)}
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
G = {}
neighbour=[]

def print_shortest_paths(parentsMap, sourceNode):
    print("Path:\n")
    for destNode in parentsMap:
        path = []
        node = destNode
        while node != sourceNode:
            if node not in parentsMap:
                print(f"No path from {sourceNode} to {destNode}")
                break
            path.append(node)
            node = parentsMap[node]
        else:
            path.append(sourceNode)
            print(f"Shortest path from {sourceNode} to {destNode}: {' -> '.join(reversed(path))}")

def print_cost(nodecost,parentmap):
    print(f'\nNew Table for {curr}:\n')
    for i in nodecost:
        print(f"{i} {nodecost.get(i)}")
    print('')
    #print_shortest_paths(parentmap,curr)

def msg_to_neighbour(msg):
    for nei in neighbour:
        n_ip=''
        n_port=ipport[nei]
        cl=socket.socket()
        try:
            cl.connect((n_ip,n_port))
            cl.send(msg.encode())
        except:
            print(f"{curr} couldn't connect with neigbour {nei} on port {n_port}")
            nodeCosts[nei]=math.inf
            msg_send(nodeCosts)
            continue
        cl.close()
def msg_parse(msg):
    fl=0

    tmp=msg
    msg=msg.split('\n')
    id,ttl=msg[0].split()
    if id==curr:
        return
    else:
        #msg_to_neighbour(tmp)
        dat=msg[1].split('@')
        for line in dat:
            try:
                src=id
                dest,weight=line.split()
            except:
                break
            fl=0
            if  nodeCosts[src]+int(weight)<nodeCosts[dest]:
                nodeCosts[dest]=nodeCosts[src]+int(weight)
                fl=1
                parentsMap[dest]=src                

     #   print('\nG updated\n')
        #print(G)
      #  parentsmap,nodecost=bellman_ford(G,curr)
      #  print_cost(nodecost,parentsmap)
        if fl==1:
            print('\n DV updated\n ')
            print_cost(nodeCosts,parentsMap)
            msg_send(nodeCosts)
        else:
            print('\nCONVERGED\n')
        


    
def msg_send(node_cost):
    try:
        id = curr + ' 60\n'
        s = ''
        for i in node_cost:
            if node_cost.get(i)==math.inf:
                continue
            s += f"{i} {node_cost.get(i)}@"
        msg = id + s
        msg_to_neighbour(msg)
    except:
        print('')



def bellman_ford(G, startingNode):
    global nodeCosts
    nodeCosts = {node: math.inf for node in G} # initialize all nodes with infinity
    global parentsMap
    parentsMap = {node: None for node in G}
    nodeCosts[startingNode] = 0

    # relax edges repeatedly
    for i in range(len(G) - 1):
        for node in G:
            for adjNode, weight in G[node].items():
                if nodeCosts[node] != math.inf and nodeCosts[node] + int(weight) < nodeCosts[adjNode]:
                    parentsMap[adjNode] = node
                    nodeCosts[adjNode] = nodeCosts[node] + int(weight)

    # check for negative-weight cycles
    for node in G:
        for adjNode, weight in G[node].items():
            if nodeCosts[node] != math.inf and nodeCosts[node] + int(weight) < nodeCosts[adjNode]:
                raise ValueError("Graph contains negative-weight cycle")

    return parentsMap, nodeCosts


def initial_strt():
    G['A']={}
    G['B']={}
    G['C']={}
    G['D']={}

    with open('init.txt', 'r') as file:
        for line in file:
            src,dest,cost=line.split()
            if src==curr:
                if src not in G:
                    G[src]={}
                if dest not in G:
                    G[dest]={}
                G[src][dest]=cost
                G[dest][src]=cost
                neighbour.append(dest)
    
    print(G)
    parentsMap, nodeCosts=bellman_ford(G,startingNode=curr)
    print_cost(nodeCosts,parentsMap)

def handle_client(conn, addr):
    data = conn.recv(1024).decode()
    msg_parse(data)

def update_graph():

    while True:  
        time.sleep(30)
        node=chr(random.randrange(65, 65 + 4))
        cost=random.randint(1,50)
        if node==curr :
            continue
        if node not in neighbour:
            continue
        print(f"Updating cost {curr} {node} {cost}")
        nodeCosts[node]=cost
        print_cost(nodeCosts,parentsMap)
        msg_send(nodeCosts)

def update_graph_inf():
    while True:
        time.sleep(20)
        print_cost(nodeCosts,parentsMap)
        print('sending dv (each 20 sec)')
        msg_send(nodeCosts)





    
        
def main():
    a=input()

    
    initial_strt()
    print("[STARTING] Server is starting")
    sock=socket.socket()
    sock.bind(('',9773))
    sock.listen()
    IP=''
    PORT=9772
    print(f"[LISTENING] sock is listening on {IP}:{PORT}.")
    time.sleep(6)   
    initial_msg_thread=threading.Thread(target=msg_send,args=(nodeCosts,))
    initial_msg_thread.start()
    update_thread=threading.Thread(target=update_graph)
    update_thread.start()
    update_thread2=threading.Thread(target=update_graph_inf)
    update_thread2.start()
    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
main()