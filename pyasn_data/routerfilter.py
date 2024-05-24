def loadfile(filename):
    file=open(filename, 'r')
    routerprefix=[]
    for line in file:
        if "::/" in line:
            prefix,tail=line[:-1].split("::/")
            length,_=tail.split("\t")
            length=int(length)//4
            prefixslice=prefix.split(":")
            prefix=""
            for slice in prefixslice:
                prefix=prefix+"0"*(4-len(slice))+slice
            print(prefix,length)


if __name__ == "__main__":
    config=dict(
        filename="/Users/teddy/Desktop/大学/网研院/work/pyasn_data/20231018.dat",
        zmap_result_path="/home/chengdaguo/scaningdata/re",
        alaised_path="/home/chengdaguo/dynamicSC/alaisedtest.txt",
        batch_depth = 1,
    )
    loadfile(config["filename"])
    