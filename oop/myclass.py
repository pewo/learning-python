#!/usr/bin/env python3

class Object:
    def __init__(self, init=None):
        print("Instansiating an object...")
        hash = dict()
        if init:
            for i in init:
                hash[i] = init[i]
        self.hash = hash

    def set(self,key,value):
        if key in self.hash:
            old = self.hash[key]
        else:
            old = None
        self.hash[key]=value
        return old

    def get(self,key):
        if key in self.hash:
            old = self.hash[key]
        else:
            old = None
        return old

    def keys(self):
        ret = []
        for key in self.hash:
            ret.append(key)
        return ret

    def data(self):
        hash = dict()
        for key in self.keys():
            hash[key] = self.get(key)
        return hash
