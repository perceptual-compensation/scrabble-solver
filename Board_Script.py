# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 23:10:37 2016

@author: PWillis
"""

b=Board(15,15,dictionary=daggad)
deck=['u','d','g',' ','s','t','n']
b.addWord("stone",7,3,0)
b.addWord("profanes",2,6,1)
b.addWord("humps",9,2,0)
b.addWord("bitty",7,1,1)
b.addWord("qi",8,0,0)
b.addWord("roll",3,6,0)
b.addWord("halvahs",1,9,1)
b.addWord("hadj",1,9,0)
b.addWord("agony",5,9,0)
b.addWord("sweat",7,9,0)
b.addWord("dingo",1,11,1)
b.addWord("goad",4,11,0)
b.addWord("clay",2,13,1)
b.addWord("od",3,14,1)
b.addWord("tiled",7,13,1)
b.addWord("revolt",9,9,0)
b.addWord("zeds",11,11,0)
b.addWord("zest",11,11,1)
b.addWord("unmeet",14,6,0)
b.addWord("rectum",4,4,1)
b.startSearch(deck)
