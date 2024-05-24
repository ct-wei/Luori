import argparse
import ipaddress
import multiprocessing
import os
from MCTS_seeded import *
from memory_profiler import profile

# @profile
# def test():
#     with open("/home/weichentian/pickle_file/Internet Service Provider (ISP).pkl", 'rb') as file:
#         head = pickle.load(file)

def add_ipv6_colon(ipv6):
    # add : to ipv6
    ipv6_list = []
    for i in range(0,len(ipv6),4):
        ipv6_list.append(ipv6[i:i+4])
    ipv6 = ":".join(ipv6_list)
    return ipv6



  
def finish_routingprefix(prefix):
    address,length=prefix.split("/")
    length=int(length)
    if length%4==0:
        return prefix
    
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

    
if __name__ == "__main__":
    routingaddress="2a03:2880:f12f::"
    length=48
    Pattern=[14,]*11
    print(Pattern)
    prefix=combine(routingaddress,length,Pattern)
    print(prefix)
    # filename=os.listdir("/home/weichentian/pickle_file")
    # num=0
    # for f in filename:
    #     a=f.split(".")[0]
    #     if a.isdigit():
    #         num+=1
    # print(num)
    # a=finish_routingprefix("2a13:a280::/127")
    # routingaddress="2a13:a280::"
    # length=25
    # Pattern=[1,2,3]
    # a=conmbine(routingaddress,length,Pattern)
    # print(a)
    
    ipv6_probes=['2001:1248:5f54:0754:a93e:ef8e:9197:a8f5', '2001:1248:5f54:1671:52c9:2fec:7d30:4c1f', '2001:1248:5f54:2b10:b30f:8900:92d2:9308', '2001:1248:5f54:304b:cee5:210e:7c38:b5a3', '2001:1248:5f54:41e4:7f69:2a9a:2829:993a', '2001:1248:5f54:5aca:5383:cee3:ab11:8f9e', '2001:1248:5f54:6ebd:67bf:3adb:3db5:8e6c', '2001:1248:5f54:7d91:4fd8:19f6:f4e1:02ac', '2001:1248:5f54:8007:9a15:0c09:2474:043e', '2001:1248:5f54:987d:f507:8842:b361:ecde', '2001:1248:5f54:a2ea:e341:668b:71db:6686', '2001:1248:5f54:b043:7a0c:910e:f439:eb66', '2001:1248:5f54:c208:3947:28a0:b498:6d41', '2001:1248:5f54:d16b:dc5b:7e9d:0719:61c5', '2001:1248:5f54:effe:1ee0:0c00:2336:cd2d', '2001:1248:5f54:f06e:9f85:9aa4:6f90:31b1']
    length=48
    find_activenode(ipv6_probes,length)
    
    