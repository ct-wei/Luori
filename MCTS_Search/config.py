date="unseed01"
scan_config=dict(

# just for seeded
routingprefixpath="routingprefix_dataset/router0603/",

# hyper para
budget_limit=20,
epsilon=0.3,
trap_n=3,
recheck_limit=1,
budget=0,

# sudo zmap passport
# input your passport here
passport="xxxxxxxxxx",
local_ipv6="xxxxxxxxxx",
  
generated_address_path="scaningdata_MCTS/un",
zmap_result_path="scaningdata_MCTS/unre",
scaninglist="work_dir/scaninglist_"+date+".txt",
fullrespond_path="work_dir/FRP_"+date+".txt",
logpath="work_dir/log_MCTS_"+date+".txt",


pickle_file='Pickle_file/',
ASfilename="Lookuptable/as_org_category.csv",
pyasnfile='pyasn_data/20240427.0200.dat',




)