

import multiprocessing
from multiprocessing.dummy import Process
import random
from Tools import combine, detectprobes, find_activenode, prefix_to_sixteen, saveprobes, send_probes,outputfullyresponsive,send_icmpv6
from MCTS_node.MCTS_Node import MCTS_Node,MCTS_Head,build_child


def is_trap(node,config):
    
    FRP_flag=0
    
    if node.V_flag==2 and node.V_k >= 16*config["trap_n"] and node.N_k >= config["trap_n"]:
        for child in node.nextnode:
            if child.V_k < 16*config["trap_n"] or child.N_k < config["trap_n"]:
                return True
            
            if child.V_flag==1:
                FRP_flag+=1
            
        if FRP_flag==16:
            return True
        
    return False


def do_simulation(node,config,head):
    routingprefix,length=head.routingprefix.split("/")
    length=int(length)
    real_address=combine(routingprefix,length,node.Pattern)
    
    ipv6_addresses=prefix_to_sixteen(real_address)
    random.shuffle(ipv6_addresses)
    
    active_set=set()
    
    print("scanning:",real_address)
    send_icmpv6(ipv6_addresses,active_set)
            

    # prefix,filename=saveprobes(ipv6_addresses,real_address,config)
    # send_probes(filename,prefix,config)
    # active_set=detectprobes(filename,config)
    
    active_node=find_activenode(active_set,length)
    if len(node.nextnode)==0:
        build_child(node)
    
    file=open(config["scanninglist"],"a")
    file.write(real_address+"\n")
    file.close()
    
    do_backup(active_set,node,active_node)
    if len(active_set)==16:
        outputfullyresponsive(real_address,config)


def backupFRP(node):
    while node.parent!=None:
        node.type="k"
        node.V_k+=16
        node.N_k+=1
        awardneighbors(node)
        node=node.parent
        
    
    node.type="k"
    node.V_k+=16
    node.N_k+=1
    
    
def awardneighbors(node):
    parent = node.parent
    for child in parent.nextnode:
        if child.type=="p":
            dist=abs(child.Pattern[-1]-node.Pattern[-1])
            child.N_p+=1
            child.V_p+=16-dist
            

    
def backup(node,V_k):
    while node.parent!=None:
        node.type="k"
        node.V_k += V_k
        node.N_k += 1        
        node=node.parent
            
        
    node.type="k"
    node.V_k += V_k
    node.N_k += 1 
    

def do_backup(active_set,node,ipv6_probes):
    if len(active_set)==16:
        node.V_flag=1
        backupFRP(node)
        return
    else:
        node.V_flag=0
        
    idx=len(node.Pattern)
    
    V_k=0
    for n in node.nextnode:
        if n.Pattern[idx-1] in ipv6_probes:
            V_k+=1
            n.N_p+=1
            n.V_p+=1
        else:
            n.N_p+=1
    
    backup(node,V_k)

if __name__ == "__main__":
    pass