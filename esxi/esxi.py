#!/usr/bin/env python3

import argparse
import glob
import ipaddress
import json
import os
import re
import readline
import socket
import sys


confd = sys.argv[0] + ".d"
debug = 0

#
# Read network info from file
# file is json lines
#
#{ "ip": "192.168.1.0", "len": "24", "gw": "192.168.1.1", "vlan": "3903" }
#{ "ip": "10.0.0.0", "len": "24", "gw": "10.0.0.1", "vlan": "10" }
#
# Everythin without a starting { is excluded

def read_netinfo(netinfo):
    res = dict()
    if debug: print("Netinfo: ", netinfo)
    try:
        f = open(netinfo,"r")
    except Exception as err:
        print(err)
        print("Cant read file ",netinfo," exiting...")
        sys.exit(1)

    lineno = 0

    for line in f:
        lineno+=1
        if not re.search("^{", line):
            if debug: print("Excluding(",lineno,"): ", line,end='')
            continue

        line = line.lower()

        if debug: print("Including(",lineno,"): ", line,end='')
        try:
            j = json.loads(line)
        except Exception as err:
            print("Can't convert line",lineno,"to json, exluding data")
            print(err)
            continue

        if debug: print("j: ", j)
        try:
            a = ipaddress.ip_network(j["ip"] + "/" + j["len"])
        except Exception as err:
            print("Can't convert line",lineno,"to ipaddress object, exluding data")
            print(err)
            continue

        #
        # Add network to hash
        #
        res[a.exploded]=j
        
        if debug: print("a: ", a.exploded)

    return res

def find_network(ip,res):
    try:
        my_ip = ipaddress.ip_network(ip + "/32")
    except Exception as err:
        print(err)
        return(None)

    for i in res:
        try:
            network = ipaddress.ip_network(i)
        except Exception as err:
            print(err)
            continue
        else:
            if my_ip.subnet_of(network):
                if debug: print("found network: ",i)
                return(network)

    if debug: print("my_ip: ", my_ip)


def get_network_keys(network,*keys):
    if debug: print("network: ", network)
    res = dict();

    for k in keys:
        if debug: print("key: ", k)
        k = k.lower()
        if k in network:
            res[k]=network[k]

    return(res)

#
# read input using GNUreadline
#
def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)  # or raw_input in Python 2
   finally:
      readline.set_startup_hook()

def is_ip(ip):
    try:
        my_ip = ipaddress.ip_network(ip + "/32")
    except Exception as err:
        print(err)
        return(None)
    else:
        return(my_ip)

def resolv_ip(ip):
    if not ip:
        return(None)
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except Exception as err:
        print("resolv_ip error: ",err)
        return(None)
    else:
        return(hostname)

def resolv_name(hostname):
    if not hostname:
        return(None)
    try:
        ip = socket.gethostbyname(socket.getfqdn(hostname))
    except Exception as err:
        print("resolv_name error: ",err)
        return(None)
    else:
        return(ip)

def get_hostname_and_ip(prompt, hostname, ip, use_default = False):
    #print("prompt: ", prompt)
    #print("hostname: ", hostname)
    #print("ip: ", ip)

    if hostname and ip:
        return(hostname, ip)

    resolved_name = hostname
    if hostname:
        resolved_name = resolv_name(hostname)

    resolved_ip = ip
    if ip:
        resolved_ip = resolv_ip(ip)

    if not hostname:
        if use_default:
            if debug: print("using default name: ", resolved_ip)
            hostname = resolved_ip
        else:
            hostname = rlinput(prompt+"name: ",resolved_ip)
        resolved_name = resolv_name(hostname)

    if not ip:
        if use_default:
            if debug: print("using default ip: ", resolved_ip)
            ip = resolved_name
        else:
            ip = rlinput(prompt+" IP address: ",resolved_name)
        resolved_ip = resolv_ip(ip)

    if not hostname:
        if debug: print("need hostname")
        hostname = rlinput(prompt+"name: ",resolved_ip)
        resolved_name = resolv_name(hostname)

    if not ip:
        if use_default and resolved_name:
            if debug: print("using default ip: ", resolved_name)
            ip = resolved_name
        else:
            if debug: print("need ip")
            ip = rlinput(prompt+"ip: ",resolved_name)
        
    return(hostname,ip)

#
# Get ip info from file
#
def get_ip_info(netinfo, ip):

    my_net = find_network(ip, netinfo)
    if my_net == None:
        print("Unable to find matching network for",ip,", exiting...")
        sys.exit(1)

    if debug: print("my_net: ", my_net)

    js = netinfo[str(my_net)]
    if debug: print("js: ", js)

    keys = get_network_keys(js,"vlan","gw")
    if debug: print("keys: ", keys)

    return(keys)

#
# Main
#
netinfo = dict()

#
# Read all files in $0.d/*.net
#
for i in glob.glob(confd + "/*.net"):
    if debug: print("Reading network config:",i)
    lnetinfo = read_netinfo(i)
    for j in lnetinfo:
        netinfo[j]=lnetinfo[j]

if debug: print("netinfo:",netinfo)

parser = argparse.ArgumentParser(description='Create inventory files.')
parser.add_argument('--hostip', type=str,  help='ip address of host')
parser.add_argument('--hostname', type=str,  help='hostname')
parser.add_argument('--idracip', type=str,  help='ip address of idrac')
parser.add_argument('--idracname', type=str,  help='name of idrac')
args = parser.parse_args()

(hostname, hostip) = get_hostname_and_ip("host", args.hostname, args.hostip, True)
print("hostname:", hostname)
print("hostip:", hostip)

#debug = 1
hostinfo = get_ip_info(netinfo, hostip)
print("gateway:", hostinfo["gw"])
print("vlan:", hostinfo["vlan"])


if args.idracname == None:
    base = hostname.split(".")
    host = base.pop(0)
    if host:
        host += "-rm"
        for i in base:
            host += "." + i

    if debug: print("host: ", host)
    args.idracname = host

(idracname, idracip) = get_hostname_and_ip("iDRAC", args.idracname, args.idracip, True)
print("idracname: ", idracname)
print("idracip: ", idracip)
idracinfo = get_ip_info(netinfo, idracip)
print("gateway:", idracinfo["gw"])
print("vlan:", idracinfo["vlan"])
sys.exit(0)
