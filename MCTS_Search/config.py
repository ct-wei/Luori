date="unseed0808"
scan_config=dict(

# just for seeded
routingprefixpath="routingprefix_dataset/router0808/",

# hyper para
budget_limit=20,
epsilon=0.3,
trap_n=3,
recheck_limit=1,
budget=0,
failing_time=0,
failing_budget=20,

generated_address_path="scanningdata_MCTS/un",
zmap_result_path="scanningdata_MCTS/unre",

scanninglist="work_dir/scanninglist_"+date+".txt",
fullrespond_path="work_dir/FRP_"+date+".txt",
logpath="work_dir/log_MCTS_"+date+".txt",


pickle_file='Pickle_file/',
ASfilename="Lookuptable/as_org_category.csv",
pyasnfile='pyasn_data/20240721.1600.dat',




)