#!/usr/bin/env python

import sys

artifacts = dict()
pvlist = dict()

def parse_pv():
    with open(sys.argv[2],"r") as fp:
        for line in fp:
            (_, p) = line.rstrip('\n').split()
            pvlist[p] = True

def parse_gavs():
    with open(sys.argv[1],"r") as fp:
        for line in fp:
            (a, g, v, x) = line.rstrip('\n').split(',',3)
            if a in artifacts:
                artifacts[a]["v"].add(v)
                artifacts[a]["g"].add(g)
                artifacts[a]["c"] = artifacts[a]["c"] + 1
            else:
                artifacts[a] = dict()
                artifacts[a]["c"] = 1
                artifacts[a]["g"] = set()
                artifacts[a]["g"].add(g)
                artifacts[a]["v"] = set()
                artifacts[a]["v"].add(v)

def lookup():
    parse_gavs()
    parse_pv()

    print("=============== vendor-product list search in gavs =========")
    with open("vp-gavs.txt", "w") as vp:
        for k,v in pvlist.items():
            if k in artifacts:
                print(k, file=vp)
            else:
                print(f"!! {k}")

    print("=============== gavs in vendor-product list =========")
    with open("gavs-vp.txt", "w") as vp:
        for k,v in artifacts.items():
            if k in pvlist:
                print(k, file=vp)
            else:
                print(f"!! {k}")

def parse_gavs_popularity():
    with open(sys.argv[1],"r") as fp:
        for line in fp:
            (a, g, v, x) = line.rstrip('\n').split(',',3)
            ga = f"{g}/{a}"
            if ga in artifacts:
                artifacts[ga] = artifacts[ga] + 1
            else:
                artifacts[ga] = dict()
                artifacts[ga] = 1
    s=sorted(artifacts.items(), key=lambda x: x[1], reverse=True)
    for k,v in s:
        if v > int(sys.argv[2]):
            print(k,v)

parse_gavs_popularity()


