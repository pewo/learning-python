#!/usr/bin/env python3
from myclass import Object

me = Object()
me.set("bepa","cepa")
for key in me.keys():
    print("key:", key)

data = me.data()
print("data:", data)

you = Object()
you = me

you.set("bepa","what")
data = you.data()
print("data:", data)

