
# -*- coding: utf-8 -*-
import time
import ipaddress
import multiprocessing
import os
import re
import secrets
import subprocess
import threading
import pandas as pd
import pyasn
from scapy.all import *

def add_ipv6_colon(ipv6):
    # add : to ipv6
    ipv6_list = []
    for i in range(0,len(ipv6),4):
        ipv6_list.append(ipv6[i:i+4])
    ipv6 = ":".join(ipv6_list)
    return ipv6

def prefix_to_sixteen(prefix):
    address,length=prefix.split("/")
    length=int(length)
    ipv6_object = ipaddress.IPv6Address(address)
    binary_representation = format(int(ipv6_object), '0128b')
    
    ipv6s=[binary_representation[:length]]*min(2**(128-length),16)
    need_complete_format="0"+str(min((128-length),4))+"b"
    
    if len(ipv6s)==1:
        ipv6s[0]=hex(int(ipv6s[0], 2))[2:]
        ipv6s[0]=add_ipv6_colon(ipv6s[0])
        return ipv6s
    else:
        for i in range(len(ipv6s)):
            
            ipv6s[i]=ipv6s[i]+format(i, need_complete_format)+''.join([bin(secrets.randbelow(2))[2] for _ in range(128-length-4)])
            # print(len(ipv6s[i]),ipv6s[i])
            ipv6s[i] = hex(int(ipv6s[i], 2))[2:]
            ipv6s[i]=add_ipv6_colon(ipv6s[i])
        return ipv6s
    
def saveprobes(ipv6_addresses,prefix,config):
    
    prefix=prefix.replace("/","_")
    filename=prefix+".txt"
    
    file = open(config["generated_address_path"]+filename,'w')        
    for ipv6_address in ipv6_addresses:
            file.write(ipv6_address+"\n")
    file.close()
            
    return prefix,filename

def initializer():
    # 将当前进程设置为非守护进程
    multiprocessing.current_process().daemon = False

def startScanning(config):
    
    print(f"Running zmap for prefix {config['prefix']}...")
    cmd = (f"sudo -S zmap --ipv6-source-ip={config['local_ipv6']} "
            f"--ipv6-target-file={config['generated_address_path']} "
            f"-o {config['zmap_result_path']} -M icmp6_echoscan -B 10M --verbosity=0")
    echo = subprocess.Popen(['echo',config['passport']], stdout=subprocess.PIPE,)
    p = subprocess.Popen(cmd, shell=True, stdin=echo.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # print(re.findall(r"\d+\.?\d*", p.communicate()[1][-10:].decode('utf-8')))
    hit_rate = re.findall(r"\d+\.?\d*", p.communicate()[1][-10:].decode('utf-8'))[0]
    print(f"Hit rate: {hit_rate}%")
    return hit_rate



def send_probes(filename,prefix,config):

    fileconfig=dict(
        generated_address_path=config["generated_address_path"]+filename,
        zmap_result_path=config["zmap_result_path"]+filename,
        prefix=prefix,
        passport=config["passport"],
        local_ipv6=config["local_ipv6"]
    )
    startScanning(fileconfig)
    

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

def load_lookuptable(filename):
    df = pd.read_csv(filename)
    as_org_category_subcategory=df[["as","org_name","category","sub_category"]]
    return as_org_category_subcategory

def preprocess(config,address):
    lookuptable=load_lookuptable(config["ASfilename"])
    
    asndb = pyasn.pyasn(config["pyasnfile"])
    asnumber,router=asndb.lookup(address)
    
    asnumdata=lookuptable["as"].values.tolist()
    asnum_router=dict()
    for asnum in asnumdata:
        routers=asndb.get_as_prefixes(asnum)
        if routers!=None:
            asnum_router[asnum]=routers
    
    data=lookuptable[lookuptable["as"]==int(asnumber)]    
    
    return lookup(data,lookuptable,asnum_router)

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


def discriminate_fullroutering(routingprefix,config):
    ipv6_addresses=prefix_to_sixteen(routingprefix)
    
    # prefix,filename=saveprobes(ipv6_addresses,routingprefix,config)
    # send_probes(filename,prefix,config)
    # active_set=detectprobes(filename,config)
    
    

    print("scanning:",routingprefix)    
    active_set=set()
    send_icmpv6(ipv6_addresses,active_set)
    
    if len(active_set)>=config["recheck_limit"] and len(active_set)<16:
        # prefix,filename=saveprobes(ipv6_addresses,routingprefix,config)
        # send_probes(filename,prefix,config)
        # re_active_set=detectprobes(filename,config)
        # active_set.update(re_active_set)
        print("rescanning:",routingprefix)
        send_icmpv6(ipv6_addresses,active_set)
        
    if len(active_set)==16:
        return True

    else:
        return False

def finish_routingprefix(prefix):
    address,length=prefix.split("/")
    length=int(length)
    if length%4==0:
        return [prefix]
    
    ipv6_object = ipaddress.IPv6Address(address)
    binary_representation = format(int(ipv6_object), '0128b')
    generate_number=2**(4-length%4)
    ipv6s=[binary_representation[:length]] * generate_number
    
    need_complete_format="0"+str(4-length%4) +"b"

    for i in range(len(ipv6s)):
        
        ipv6s[i]=ipv6s[i]+format(i, need_complete_format)+"0"*(128-length-(4-length%4))
        ipv6s[i] = hex(int(ipv6s[i], 2))[2:]
        ipv6s[i]=add_ipv6_colon(ipv6s[i])
        ipv6s[i]=ipaddress.IPv6Address(ipv6s[i]).compressed+"/"+str(length+4-length%4)
    return ipv6s

def find_activenode(ipv6_probes,length):
    active_nodes=set()
    for ipv6_probe in ipv6_probes:
        ipv6_object=ipaddress.IPv6Address(ipv6_probe)
        binary_representation = format(int(ipv6_object), '0128b')
        active_node=binary_representation[length:length+4]
        active_nodes.add(int(active_node,2))
    return active_nodes

def load_checked_routingset(scan_config):
    # load checked_routingset
    checked_routingset=set()
    if os.path.exists(scan_config["logpath"]):
        file=open(scan_config["logpath"])
        for line in file:
            slices=line.split(" ")
            for slice in slices:
                if "/" in slice:
                    checked_routingset.add(slice)
                    break
    return checked_routingset


def outputfullyresponsive(hex_address,config):
    config['budget_limit']+=1
    config["flag"]=True
    print("found fully responsive:",hex_address)
    file = open(config["fullrespond_path"], 'a')
    file.write(hex_address + "\n")
    file.close()


def combine(routingaddress,length,Pattern):
    length=int(length)
    pattern=""
    for ch in Pattern:
        pattern=pattern+format(ch, '04b')
    pattern_len=len(Pattern)*4
    
    ipv6_object=ipaddress.IPv6Address(routingaddress)
    binary_representation = format(int(ipv6_object), '0128b')
    
    det_address=binary_representation[:length]+pattern
    det_address=det_address+"0"*(128-len(det_address))
    prefix=ipaddress.IPv6Address(int(det_address,2)).compressed
    
    return prefix+"/"+str(pattern_len+length)

def ping(ip):
    try:
        result = subprocess.Popen(
            'ping -c 1 {}'.format(ip),  # 要执行的命令。
            shell=True,  # 使用shell来执行命令。
            close_fds=True,  # 在子进程执行前关闭所有文件描述符，除了stdin, stdout, stderr。
            stdout=subprocess.PIPE,  # 子进程的标准输出。
            stderr=subprocess.PIPE   # 子进程的标准错误输出。
        )

        stdout, stderr = result.communicate()
        
        if result.returncode == 0:
            result=True
        else:
            result=False
            
    except Exception as e:
        print("执行Ping命令时发生错误:", e)
        
    return result

# def send_icmpv6(ips,result_set):
#     for ip in ips:
#         if ping(ip):
#             result_set.add(ip)
        
   
#     return result_set

def send_icmpv6(target_ipv6s,result_set):
    threads=[]        #deposit thresds
    conf.verb = 0
    
    # print(target_ipv6s)
    for target_ipv6 in target_ipv6s:    #create an instance of an object
        t=threading.Thread(target=make_icmpv6,args=(target_ipv6,result_set))
        threads.append(t)

    for thread in threads:    #start threads
        time.sleep(1.5)
        thread.start()

    for thread in threads:    # wait for all
        thread.join()       # threads to finish
    
    return result_set

def make_icmpv6(target_ipv6,result_set):
    t=1
    # 构造ICMPv6 Echo Request包
    for _ in range(t):
        try:
            pkt = IPv6(dst=target_ipv6) / ICMPv6EchoRequest()
            # 发送包并接收响应
            reply=sr1(pkt, verbose=False,timeout=1)
            if reply and ICMPv6EchoReply in reply:
                result_set.add(target_ipv6)
                return
            
                    
        except Exception as e:
            print("sending ICMPv6 error",e)
        

if __name__ == "__main__":
    # print(prefix_to_sixteen("2001:250:7809::/48"))
    ip="2c0f:ff40:0030:0282:4295:25fa:9474:27e2"
    ips=['2a09:b686:6006:832b:dce2:8266:5247:8649', '2a09:b686:600f:afa0:0b18:890a:5082:c4cb', '2a09:b686:6012:3f65:e28a:8aa2:c01a:f6a3', '2a09:b686:601f:2009:95f6:3d3b:af80:edb5', '2a09:b686:6026:f274:e9a0:2723:5e78:e620', '2a09:b686:602f:bc36:c46e:8d11:18cb:1601', '2a09:b686:6031:a490:01d0:bc81:6a2a:9539', '2a09:b686:603b:7d29:b9b7:797d:bdf2:d9fc', '2a09:b686:6043:4d8b:7fa8:b23d:f93b:cf22', '2a09:b686:6049:8b51:6d48:5afe:c16c:8b87', '2a09:b686:6054:d6b3:0cd5:0f1b:9390:97d3', '2a09:b686:605f:3d4e:f366:d760:2694:d22f', '2a09:b686:6066:39e9:01d1:5575:32e2:e5d8', '2a09:b686:6069:6922:77a3:f12c:1948:d513', '2a09:b686:6076:ec90:d32d:6fc2:69fe:d574', '2a09:b686:607e:ad62:505e:732c:d860:bdf8']
    # ips=[' 2001:0250:7809:0e69:8637:99bd:c83c:d6cc']

    result_set=set()
    # make_icmpv6(ip,result_set)
    
    start_time = time.time()  # 获取开始时间
    send_icmpv6(ips,result_set)
    end_time = time.time()  # 获取结束时间
    print("执行时间：", end_time - start_time, "秒")
    print(len(result_set))
    
    
    
    