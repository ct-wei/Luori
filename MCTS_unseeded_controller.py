import argparse
import ipaddress
import multiprocessing
import os
import random
import subprocess
import sys
import time
import pandas as pd
from Tools import initializer, send_probes,load_checked_routingset
import pickle
import pyasn
sys.path.append('.')
from copy import deepcopy
import secrets
from MCTS_node.MCTS_Node import MCTS_Node,MCTS_Head,build_child,findchild
from Tools import prefix_to_sixteen
from MCTS_unseeded import *
from config import scan_config


class MCTS_Searcher(object):
    def __init__(self):
        pass

    def worker(self,routingprefix,Tree_Type,scan_config):
        self.routingprefix=routingprefix
        self.Tree_Type=Tree_Type
        MCTSsearch(routingprefix,Tree_Type,scan_config)

    @staticmethod
    def err_call_back(err):
        print(f'error：{str(err)}')


def load_lookuptable(filename):
    df = pd.read_csv(filename)
    as_org_category_subcategory=df[["as","org_name","category","sub_category"]]
    return as_org_category_subcategory


def generate_as_router_dict(scan_config):
    # generate as_router dict
    lookuptable=load_lookuptable(scan_config["ASfilename"])
    asndb = pyasn.pyasn(scan_config["pyasnfile"])
    
    asnumdata=lookuptable["as"].values.tolist()
    asnum_router=dict()
    for asnum in asnumdata:
        routers=asndb.get_as_prefixes(asnum)
        if routers!=None:
            asnum_router[asnum]=routers
    
    return asnum_router,lookuptable

def load_seededroutings(scan_config):
    seededroutingprefix=set()
    routingprefixpath=os.listdir(scan_config["routingprefixpath"])
    for routingprefix in routingprefixpath:
        routingprefix,_=routingprefix.split(".")
        routingprefix=routingprefix.replace("_","/")
        seededroutingprefix.add(routingprefix)
    return seededroutingprefix


class RoutingPrefixIterator():
    def __init__(self,scan_config) -> None:
        self.scan_config=scan_config
        self.file=open(self.scan_config["pyasnfile"], 'r')
        self.checked_routingset=load_checked_routingset(scan_config)
        self.filenames=os.listdir(scan_config['pickle_file'])
        self.asnum_router,self.lookuptable=generate_as_router_dict(scan_config)
        self.seededroutingprefix=load_seededroutings(scan_config)
        # print(self.seededroutingprefix)
        
    def __iter__(self):
        
        return self
    
    
    def get_next(self):
        try:
            line = self.file.readline()
            while ";" in line:
                line = self.file.readline()
                
            routingprefix,asnum=line[:-1].split("\t")
            while routingprefix in self.checked_routingset or routingprefix in self.seededroutingprefix:
                line = self.file.readline()
                routingprefix,asnum=line[:-1].split("\t")
            return routingprefix,asnum
        except IndexError:
            raise StopIteration
        except ValueError:
            raise StopIteration
    
    
    def __next__(self):
        
        routingprefix,asnum=self.get_next()
        # print(routingprefix,asnum)
        Tree_Type="failing"
        transfer_level="failing"
        
        # asnum
        if str(asnum)+".pkl" in self.filenames:
            Tree_Type=str(asnum)
            transfer_level="AS"
            
            
        elif not self.lookuptable[self.lookuptable["as"]==int(asnum)].empty:
            org_name=self.lookuptable[self.lookuptable["as"]==int(asnum)].iloc[0,1]
            sub_category=self.lookuptable[self.lookuptable["as"]==int(asnum)].iloc[0,3]
            category=self.lookuptable[self.lookuptable["as"]==int(asnum)].iloc[0,2]
            
            # org_name
            if str(org_name)+".pkl" in self.filenames:
                Tree_Type=str(org_name)
                transfer_level="org"
                
            # sub_category
            elif str(sub_category)+".pkl" in self.filenames:
                Tree_Type=str(sub_category)
                transfer_level="sub_category"
            
            # category
            elif str(category)+".pkl" in self.filenames:
                Tree_Type=str(category)
                transfer_level="category"
                        
        Tree_Type=Tree_Type.replace("/","_")
        return routingprefix,Tree_Type,transfer_level


# @profile
def do_main_job(scan_config):

    num_processes = 200  # 设置想要同时运行的进程数量
    

    pool = multiprocessing.Pool(num_processes,initializer=initializer)
    
    
    # MCTS_Searcher
    searcher = MCTS_Searcher()

    routingprefixiterator=RoutingPrefixIterator(scan_config)
    
    import time

    start_time = time.time()  # 获取开始时间
    file=open(scan_config["scanninglist"],"a")
    file.write(str(start_time)+"\n")
    file.close()
    
    for routingprefix,Tree_Type,transfer_level in routingprefixiterator:

        if Tree_Type!="failing":
            pool.apply_async(
                searcher.worker,
                args=(routingprefix,Tree_Type,scan_config),
                error_callback=searcher.err_call_back
            )
    
    pool.close()
    pool.join()
    
    end_time = time.time()  # 获取结束时间
    file=open(scan_config["scanninglist"],"a")
    file.write(str(end_time)+"\n")
    file.close()

    print("执行时间：", end_time - start_time, "秒")
    
    
    
if __name__ == "__main__":
    
    do_main_job(scan_config)
    
    

    