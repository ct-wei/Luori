import os
import multiprocessing
import pandas as pd
import pyasn
import ipaddress
from copy import deepcopy
import pickle
from MCTS_Search.MCTS_node.MCTS_Node import MCTS_Node,MCTS_Head
import random
from pickle_Iterator import pickleIterator
from pickle_config import scan_config

class PickleMaker(object):
    def __init__(self):
        pass

    def worker(self,scan_config,transfer_name,lookuptable,asnum_router,type):
        make_pickle_file(scan_config,transfer_name,lookuptable,asnum_router,type)


    @staticmethod
    def err_call_back(err):
        
        print(f'error：{str(err)}')
        

def do_transfer(config,routingprefixes):
    
    pattern_set=set()

    for routingprefix in routingprefixes:
        _,routing_length=routingprefix.split("/")
        routing_length=int(routing_length)
        routingprefix=routingprefix.replace("/","_")
        if os.path.exists(config["routingprefixpath"]+routingprefix+".txt"):
            file=open(config["routingprefixpath"]+routingprefix+".txt")
            for line in file:
                
                ipv6_address,seed_length=line[:-1].split("/")
                ipv6_object = ipaddress.IPv6Address(ipv6_address)
                binary_representation = format(int(ipv6_object), '0128b')
                seed_length=int(seed_length)
                
                pattern=binary_representation[routing_length:seed_length]
                pattern_set.add(pattern)
                
    hex_pattern_set=set()
    for pattern in pattern_set:
        if pattern!="":
            hex_pattern=transpattern(pattern)
            hex_pattern_set.add(hex_pattern)
        
    
    return hex_pattern_set

def transpattern(pattern):
    pattern=pattern+"000"
    hex_pattern=""
    for idx in range(len(pattern)//4):
        hex_pattern=hex_pattern+format(int(pattern[4*idx:4*idx+4],2), 'x')
    return hex_pattern


def lookupAS(asnums,asnum_router):
    allrouters=set()
    for asnum in asnums:
        if asnum in asnum_router:
            for item in asnum_router[asnum]:
                allrouters.add(item)
    return allrouters


def lookup(data,lookuptable,asnum_router):
    # orgnized routers
    org=data.iloc[0,1]
    asnums=lookuptable[lookuptable["org_name"]==org]["as"].values.tolist()
    routers=lookupAS(asnums,asnum_router)
        
    # un-orgnized routers
    if len(routers)==0:
        sub_category=data.iloc[0,3]
        asnums=lookuptable[lookuptable["sub_category"]==sub_category]["as"].values.tolist()
        routers=lookupAS(asnums,asnum_router)

                            
        # un-sub_category routers 
        if len(routers)==0:
            category=data.iloc[0,2]
            asnums=lookuptable[lookuptable["category"]==category]["as"].values.tolist()
            routers=lookupAS(asnums,asnum_router)
    
    return routers


  
  
  

def get_seeds_data_AS(asnum,lookuptable,asnum_router):
        
    # do transfer
        seeds_data=set()
                
        # data=[as,org_name,country,category,sub_category]
        data=lookuptable[lookuptable["as"]==int(asnum)]
        
        # try to transfer in AS level
        routers=asnum_router[asnum]
        seeds_data=do_transfer(scan_config,routers)
        
        if len(seeds_data)==0:
            transfer_flag=False
            return seeds_data,transfer_flag
            
        else:
            # successfully transfer
            transfer_flag=True
        
        return seeds_data,transfer_flag
    
    
    
def get_seeds_data(transfer_name,lookuptable,asnum_router,type,config):
    
    transfer_flag=True
    asnums=lookuptable[lookuptable[type]==transfer_name]["as"].values.tolist()
    routers=lookupAS(asnums,asnum_router)
    seeds_data=do_transfer(scan_config,routers)
    
    if len(seeds_data)==0:
        transfer_flag=False
        return seeds_data,transfer_flag


    # random select k element
    num_elements_to_select = min(config["random_select_k"],len(seeds_data))

    #  randomly sample
    selected_elements = random.sample(seeds_data, num_elements_to_select)

    return selected_elements,transfer_flag



def build_child(node):
    
    buildspace=[i for i in range(16)]
    for ch in buildspace:
        pattern=deepcopy(node.Pattern)
        
        pattern.append(ch)
        child=MCTS_Node(pattern,node)
        node.expand(child)
        
        

def findchild(seed,head,idx):
    for node in head.nextnode:
        if node.Pattern[idx]==seed[idx]:
            return node
    return None



def awardneighbors(seed,head,idx,score):
    
    for node in head.nextnode:
        if node.type=="p":
            dist=abs(node.Pattern[idx]-seed[idx])
            node.N_p+=1
            node.V_p+=16-dist
                        
            
            
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
    node.type="k"
    backupFRP(node)
    
    
def awardneighbors(node):
    parent = node.parent
    for child in parent.nextnode:
        if child.type=="p":
            dist=abs(child.Pattern[-1]-node.Pattern[-1])
            child.N_p+=1
            child.V_p+=16-dist

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



def trans_seeds_data(seeds_data):
    seeds=[]
    for seed in seeds_data:
        tens=[]
        for ch in seed:
            tens.append(int(ch,16))
        seeds.append(tens)
    return seeds
        
        
        
def make_pickle_file(config,transfer_name,lookuptable,asnum_router,type):
    if type=="as":
        seeds_data,transfer_flag=get_seeds_data_AS(transfer_name,lookuptable,asnum_router)
    else:
        seeds_data,transfer_flag=get_seeds_data(transfer_name,lookuptable,asnum_router,type,config)
        
    # Only transfer the transferable
    if transfer_flag:
        seeds_data=trans_seeds_data(seeds_data)
        head=MCTS_Head(transfer_name)
        for seed in seeds_data:
            buildSeed(seed,head)
            
        with open(config['pickle_file']+str(transfer_name)+'.pkl', 'wb') as file:
            pickle.dump(head, file)
            

    
if __name__ == "__main__":
       
    # make pickle
    num_processes = 100
    
    pool = multiprocessing.Pool(num_processes)

    # AS_PickleMaker
    picklemaker=PickleMaker()
    pickleiterator=pickleIterator(scan_config)
    
    for item in pickleiterator:
        scan_config,built_name,lookuptable,asnum_router,built_type=item
        pool.apply_async(
            picklemaker.worker,
            args=(scan_config,built_name,lookuptable,asnum_router,built_type),
            error_callback=picklemaker.err_call_back
        )

    pool.close()
    pool.join()

    

    

    
        

    


    
        
    
    

            