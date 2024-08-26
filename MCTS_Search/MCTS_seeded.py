import argparse
import ipaddress
import multiprocessing
import os
import random
import subprocess
import sys
import time
import pandas as pd
from Tools import combine, find_activenode, send_probes,discriminate_fullroutering
from Strategy import do_backup,is_trap,do_simulation
import pickle
import pyasn
sys.path.append('.')
from copy import deepcopy
import secrets
from MCTS_node.MCTS_Node import MCTS_Node,MCTS_Head,build_child,findchild
from Tools import prefix_to_sixteen,saveprobes,outputfullyresponsive
from config import scan_config




def get_seeded(routingprefix,head,Tree_Type,config):
    seed_flag=False
    pattern_set=set()
    _,routing_length=routingprefix.split("/")
    routing_length=int(routing_length)
    routingprefix=routingprefix.replace("/","_")
    
    seededfile=open(config["routingprefixpath"]+routingprefix+".txt")
    for line in seededfile:
        
        ipv6_address,seed_length=line[:-1].split("/")
        # ipv6_address=trans_truncation(seed_prefix)
        
        ipv6_object = ipaddress.IPv6Address(ipv6_address)
        binary_representation = format(int(ipv6_object), '0128b')
        seed_length=int(seed_length)
        
        pattern=binary_representation[routing_length:seed_length]
        pattern_set.add(pattern)
        seed_flag=True
    
    hex_pattern_set=set()
    for pattern in pattern_set:
        if pattern!="":
            hex_pattern=transpattern(pattern)
            hex_pattern_set.add(hex_pattern)
        
    return hex_pattern_set,seed_flag
    
def transpattern(pattern):
    pattern=pattern+"000"
    hex_pattern=""
    for idx in range(len(pattern)//4):
        hex_pattern=hex_pattern+format(int(pattern[4*idx:4*idx+4],2), 'x')
    return hex_pattern

def trans_seeds_data(seeds_data):
    seeds=[]
    for seed in seeds_data:
        tens=[]
        for ch in seed:
            tens.append(int(ch,16))
        seeds.append(tens)
    return seeds


def init_seeded_Node(routingprefix,head,Tree_Type,config):
        
    seeds_data,seed_flag=get_seeded(routingprefix,head,Tree_Type,config)
    seeds_data=trans_seeds_data(seeds_data)
    for seed in seeds_data:
        buildSeed(seed,head)
    if seed_flag==True and len(seeds_data)==0:
        head.V_flag=1
    return head

def buildSeed(seed,head):
    # absolute frp 1
    # possible frp 2

    node=head

    for idx in range(len(seed)):
        if node.nextnode==[]:
            build_child(node)
        child=findchild(seed,node,idx)
        node=child
        
    # set the deepest node known
    node.V_flag=1
  


        
    
def is_satisfied(config,head):
    if config['budget']<config["budget_limit"] and head.V_flag!=1 and config['failing_time']<config['failing_budget']:
        return True
    return False

def is_nonterminal(head,node):
    _,length=head.routingprefix.split("/")
    length=int(length)
    return len(node.Pattern)*4+length<=124

def isfullyexpanded(node):
    return len(node.nextnode)==16

def haschild(node,pattern):
    for child in node.nextnode:
        if child.Pattern==pattern:
            return True
    return False

def expand(node):
    searchingspace=[i for i in range(16)]
    for ch in searchingspace:
        pattern=deepcopy(node.Pattern)
        pattern[node.depth]=ch
        if not haschild(node,pattern):
            newnode=MCTS_Node(pattern,node)
            node.expand(newnode)

            return newnode
        
def bestchild(node,epsilon):
    if node.V_flag==1:
        return "Retry"
    
    # choose the max known node
    if random.random()>epsilon:
        # print("k")
        valuels=[]
        for child in node.nextnode:
            valuels.append(getvalue(child,"k"))
       
       
    # choose the max potential node 
    else:
        # print("p")
        valuels=[]
        for child in node.nextnode:
            valuels.append(getvalue(child,"p"))
    
    if sum(valuels)==0:
        # print(valuels)
        # print(node.Pattern)
        return "Retry"

    max_id=valuels.index(max(valuels))
    return  node.nextnode[max_id]



def getvalue(child,type):
    if type==child.type and type=="p" :
        score=child.V_p/child.N_p * abs(child.V_flag-1)
    elif type==child.type and type=="k" :
        score=child.V_k/child.N_k * abs(child.V_flag-1)
    else:
        score=0
    return score


        


def Treepolicy(head,config):
    node=head
    epsilon=config["epsilon"]
    
    if is_trap(node,config):
        return node
        
    while is_nonterminal(head,node):
        node=bestchild(node,epsilon)
        
        if node=="Retry":
            # breakpoint()
            return "Retry"
        
        if is_trap(node,config):
            return node
        
        if not isfullyexpanded(node):
            return node 

    return node
        
def Defaultpolicy(node,config,head):
    if is_nonterminal(head,node):
        return do_simulation(node,config,head)
    else:
        return 0

    


           


    
def backup(node,V_k):
    while node.parent!=None:
        node.type="k"
        node.V_k += V_k
        node.N_k += 1        
        node=node.parent
            
        
    node.type="k"
    node.V_k += V_k
    node.N_k += 1 
        


# @profile
def MCTSsearch(routingprefix,Tree_Type,config):
    # 从文件读取对象并反序列化
    with open(config['pickle_file']+str(Tree_Type)+'.pkl', 'rb') as file:
        head = pickle.load(file)
        head.routingprefix=routingprefix
    
    if not discriminate_fullroutering(routingprefix,config):
    
        head=init_seeded_Node(routingprefix,head,Tree_Type,config)
        # first scan for 500 times
        while is_satisfied(config,head):
            node=Treepolicy(head,config)
            
            if node!="Retry":
                Defaultpolicy(node,config,head)
                config['budget']+=1
                config['failing_time']=0
            else:
                config['failing_time']+=1
                
        
        
    file=open(config["logpath"],"a")
    file.write("prefix:%50s"%str(routingprefix)+"  budget:%20s"%config["budget"]+"\n")
    file.close()




    


if __name__ == "__main__":
    
    
    parser = argparse.ArgumentParser(description='Demo of argparse')
    
    parser.add_argument('--routingprefix', type=str, default="240e:983:1e00::/40")
    parser.add_argument('--Tree_Type', type=str, default="58466")
    
    args = parser.parse_args()
    routingprefix = args.routingprefix
    Tree_Type = args.Tree_Type

    
    
    import time

    start_time = time.time()  # get the start time
    file=open(scan_config["scanninglist"],"a")
    file.write(str(start_time)+"\n")
    file.close()
    
    MCTSsearch(routingprefix,Tree_Type,scan_config)
    
    end_time = time.time()  # get the end time
    file=open(scan_config["scanninglist"],"a")
    file.write(str(end_time)+"\n")
    file.close()

    print("running time", end_time - start_time, "seconds")
    
    

    
