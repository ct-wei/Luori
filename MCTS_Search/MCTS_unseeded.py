import argparse
import ipaddress
import multiprocessing
import os
import random
import subprocess
import sys
import time
import pandas as pd
from Tools import discriminate_fullroutering, send_probes
import pickle
import pyasn
sys.path.append('.')
from copy import deepcopy
import secrets
from MCTS_node.MCTS_Node import MCTS_Node,MCTS_Head,build_child,findchild
from Tools import prefix_to_sixteen,saveprobes,combine,find_activenode,outputfullyresponsive
from Strategy import do_backup, do_simulation,is_trap
from config import scan_config



def init_MCTS_Node(routingprefix,head):
    
    head.routingprefix=routingprefix
        
    return head


        
        
    
def is_satisfied(config):
    if config['budget']<config["budget_limit"]:
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
        return "FRP"
    
    # choose the max known node
    if random.random()>epsilon:
        valuels=[]
        for child in node.nextnode:
            valuels.append(getvalue(node,child,"k"))
       
       
    # choose the max potential node 
    else:   
        valuels=[]
        for child in node.nextnode:
            valuels.append(getvalue(node,child,"p"))
            
    if sum(valuels)==0:
        return "FRP"

    max_id=valuels.index(max(valuels))
    return  node.nextnode[max_id]



def getvalue(node,child,type):
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
        if node=="FRP":
            return "FRP"
        
        if not isfullyexpanded(node):
            return node 

    return node
        
def Defaultpolicy(node,config,head):
    if is_nonterminal(head,node):
        return do_simulation(node,config,head)
    else:
        return 0






def MCTSsearch(routingprefix,Tree_Type,config):
    # 从文件读取对象并反序列化
    with open(config['pickle_file']+str(Tree_Type)+'.pkl', 'rb') as file:
        head = pickle.load(file)
        
        
    if not discriminate_fullroutering(routingprefix,config):
    
        head=init_MCTS_Node(routingprefix,head)
        # first scan for 500 times
        while(is_satisfied(config)):
            node=Treepolicy(head,config)
            config['budget']+=1
            if node!="FRP":
                Defaultpolicy(node,config,head)
    
        
    file=open(config["logpath"],"a")
    file.write("prefix:%50s"%str(routingprefix)+"  budget:%20s"%config["budget"]+"\n")
    file.close()

    
def detectprobes(filename,config):
    fileconfig = dict(
        zmap_result_path=config["zmap_result_path"] + filename,
        passport=config["passport"],
        local_ipv6=config["local_ipv6"]
    )
    echoprobes = open(fileconfig["zmap_result_path"], 'r')
    
    active_set=set()

    for probe in echoprobes:
        ipv6_object = ipaddress.IPv6Address(probe[:-1])
        address=ipv6_object.exploded
        active_set.add(address)

    return active_set
    

if __name__ == "__main__":
    
    

    parser = argparse.ArgumentParser(description='Demo of argparse')
    
    parser.add_argument('--routingprefix', type=str, default="2803:f800:50::/45")
    parser.add_argument('--Tree_Type', type=str, default="38")
    
    args = parser.parse_args()
    routingprefix = args.routingprefix
    Tree_Type = args.Tree_Type
    

    MCTSsearch(routingprefix,Tree_Type,scan_config)

    

    