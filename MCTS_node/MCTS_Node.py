from copy import deepcopy


class MCTS_Node():
    def __init__(self,pattern,parent):
        self.parent=parent
        self.Pattern=pattern
        self.nextnode=[]
        
        self.V_flag=2 # -1/Partially Active  0/UN-FRP  1/FRP  2/Uncertain 
        
        self.type="p"
        self.N_k=0
        self.N_p=0
        
        self.V_k=0
        self.V_p=0
        
    
    def expand(self,node):
        self.nextnode.append(node)
        
        
class MCTS_Head(MCTS_Node):
    
    def __init__(self,Tree_type,routingprefix=None):
        super().__init__(pattern=[],parent=None)
        self.V_flag=0
        self.Tree_type=Tree_type
        self.routingprefix=routingprefix


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

if __name__ == "__main__":
    mcts_head=MCTS_Head(111)
    print(mcts_head.V_flag)
    
            