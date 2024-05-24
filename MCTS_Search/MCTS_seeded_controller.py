import argparse
import ipaddress
import multiprocessing
import os
import random
import subprocess
import sys
import time
import pandas as pd
from Tools import send_probes,finish_routingprefix,load_checked_routingset
import pickle
import pyasn
sys.path.append('.')
from copy import deepcopy
import secrets
from MCTS_node.MCTS_Node import MCTS_Node,MCTS_Head,build_child,findchild
from Tools import prefix_to_sixteen
from MCTS_seeded import *
from config import scan_config


class MCTS_Searcher(object):
    def __init__(self):
        pass

    def worker(self,routingprefix,Tree_Type,scan_config):
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



class SeededPrefixIterator():
    def __init__(self,scan_config) -> None:
        self.scan_config=scan_config
        self.asndb = pyasn.pyasn(scan_config["pyasnfile"])
        self.checked_routingset=load_checked_routingset(scan_config)
        self.filenames=os.listdir(scan_config['pickle_file'])
        self.routingprefixpath=os.listdir(scan_config["routingprefixpath"])
        # print(len(self.checked_routingset))
            
    def __iter__(self):
        
        return self
    

    def get_next(self):
        try:
            routingprefixpath=self.routingprefixpath.pop(0)
            
            routingprefix,_=routingprefixpath.split(".")
            routingprefix=routingprefix.replace("_","/")
            
            return routingprefix

        except IndexError:
            raise StopIteration
        except ValueError:
            raise StopIteration
            
    def is_legal(self,routingprefix):

        if routingprefix in self.checked_routingset:
            return False
        elif routingprefix=="None":
            return False
        return True
    
    
    def __next__(self):
        routingprefix=self.get_next()
        while not self.is_legal(routingprefix):
            routingprefix=self.get_next()

        routingaddress,_=routingprefix.split("/")
        
        asnum,_=self.asndb.lookup(routingaddress)
                
        Tree_Type="failing"
        transfer_level="failing"
        
        # asnum
        if str(asnum)+".pkl" in self.filenames:
            Tree_Type=str(asnum)
            transfer_level="AS"
                                    
        Tree_Type=Tree_Type.replace("/","_")
        return routingprefix,Tree_Type,transfer_level


        


# @profile
def do_main_job(scan_config):

    num_processes = 100  # 设置想要同时运行的进程数量
    
    pool = multiprocessing.Pool(num_processes)
    
    
    # MCTS_Searcher
    searcher = MCTS_Searcher()

    routingprefixiterator=SeededPrefixIterator(scan_config)
    
    for routingprefix,Tree_Type,transfer_level in routingprefixiterator:

        if transfer_level!="failing":
            # print(routingprefix,Tree_Type,transfer_level)
            
            pool.apply_async(
                searcher.worker,
                args=(routingprefix,Tree_Type,scan_config),
                error_callback=searcher.err_call_back
            )
    
    pool.close()
    pool.join()
    
    
    
if __name__ == "__main__":
    
    do_main_job(scan_config)
    
    

    