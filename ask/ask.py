#!/usr/bin/env python3

import sys
import argparse
import re
import json
import yaml
import os

def get_whatever(prompt):
    inp = input(prompt + ": ")
    if inp:
        inp.strip()
    return inp

def get_string(prompt):
    inp = get_whatever("(string) " + prompt)
    if inp:
        inp.strip()
    return inp

def isfloat(x):
    try:
        a = float(x)
    except:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except:
        return False
    else:
        return a == b

def get_float(prompt):
    while True:
        inp = get_whatever("(float) " + prompt )
        if inp:
            inp.strip()

        if len(inp) < 1:
            return None
        
        if isfloat(inp):
            return inp
        else:
            print("Input is not an float")

def get_integer(prompt):
    while True:
        inp = get_whatever("(integer) " + prompt )
        if inp:
            inp.strip()

        if len(inp) < 1:
            return None
        
        if inp.isnumeric():
            return inp
        else:
            print("Input is not an integer")

def get_array(prompt):
    ret = []
    print("Input array, one item per line, end with empty line")
    while True:
        inp = get_whatever("(array) " + prompt )
        if not inp:
            break
        #print("adding: ",inp)
        ret.append(inp)

    return ret


parser = argparse.ArgumentParser(description='Ask.')
parser.add_argument('-t','--template', type=str, help="Which template to use for input", required=True)
parser.add_argument('--save', type=str, help="Filename to save yaml output", required=True)

args = parser.parse_args()

#print("template:",args.template)
#print("save:",args.save)

basename = os.path.basename(args.template)
#print("basename:",basename)

try:
    f = open(args.template)
except Exception as err:
    print(err)
    exit(1)

json = dict()

while True:
    data = f.readline()
    if not data:
        break

    data.strip()
    line = data.splitlines()
    data = line.pop(0)
    mydo = data.split("#")
    cmdline = mydo.pop(0)
    if not cmdline:
        continue

    #print("cmdline:",cmdline)
    todo = cmdline.split(":")
    cmd = todo.pop(0)
    #print("cmd:",cmd)
    cmd_type = todo.pop(0)

    if "string" in cmd_type or not len(cmd_type) > 1:
        my_string = get_string(cmd)
        json[cmd]=my_string

    elif "float" in cmd_type: 
        my_string = get_float(cmd)
        if my_string != None:
            if isint(my_string):
                json[cmd]=int(my_string)
            else:
                json[cmd]=float(my_string)

    elif "integer" in cmd_type: 
        my_string = get_integer(cmd)
        if my_string != None:
            json[cmd]=int(my_string)

    elif "array" in cmd_type:
        my_arr = get_array(cmd)
        json[cmd]=my_arr

    elif "dict" in cmd_type:
        keys = cmd_type.split("=")
        bepa = keys.pop(0)
        my_dict = dict()
        found_keys = 0
        for key in keys:
            if len(key) > 1:
                for subkey in key.split(","):
                    found_keys += 1
                    my_var = get_string(subkey)
                    if len(my_var) > 1:
                        my_dict[subkey]=my_var

        if found_keys > 0:
            json[cmd]=my_dict

#print("json:",json)
#print(yaml.dump(json))
ret = dict()
ret[basename]=json
print("Exporting:")
print(yaml.dump(ret))
