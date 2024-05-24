
import os
from pathlib import Path
import pandas as pd
import pyasn
from pickle_config import scan_config

class pickleIterator():
    def __init__(self,scan_config) -> None:
        self.scan_config=scan_config
        self.asndb = pyasn.pyasn(scan_config["pyasnfile"])
        self.asnum_router,self.lookuptable=generate_as_router_dict(scan_config)
        
        self.asnum=list(self.asnum_router.keys())
        self.org_name=set(self.lookuptable["org_name"].values.flatten())
        self.sub_category=set(self.lookuptable["sub_category"].values.flatten())
        self.category=set(self.lookuptable["category"].values.flatten())
        
        self.index = 0
        
    def __iter__(self):
        return self
    

    def __next__(self):
        
        built_name,built_type=self.get_next()
        
        while(self.is_built(built_name)):
            built_name,built_type=self.get_next()
        if type(built_name)==int:
            pass
        else:
            built_name=str(built_name).replace("/","_")
        
        return self.scan_config,built_name,self.lookuptable,self.asnum_router,built_type
    
    def get_next(self):
        if self.index < len(self.asnum):
            asnum = self.asnum[self.index]
            self.index += 1

            return asnum, "as"
        else:
            if self.org_name:
                org_name=self.org_name.pop()
                return org_name, "org_name"
            
            if self.sub_category:
                sub_category=self.sub_category.pop()
                return sub_category, "sub_category"

            if self.category:
                category=self.category.pop()
                return category, "category"
            
        raise StopIteration

    def is_built(self,built_name):
        
        path=Path(self.scan_config['pickle_file']+str(built_name)+'.pkl').resolve()
        return path.exists()


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
    
    
def load_lookuptable(filename):
    df = pd.read_csv(filename)
    as_org_category_subcategory=df[["as","org_name","category","sub_category"]]
    return as_org_category_subcategory




if __name__ =="__main__":
    pickleiterator=pickleIterator(scan_config)

    for item in pickleiterator:
       scan_config,built_name,lookuptable,asnum_router,built_type=item
       print(built_name)
       