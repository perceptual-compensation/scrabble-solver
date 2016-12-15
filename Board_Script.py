# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 23:10:37 2016

@author: PWillis
"""

b = Board(15,15,dictionary=daggad)
deck=['w','e','k','u','t',' ','i']
b.addWord("minxes",7,5,0)
b.addWord("unfit",6,7,1)
b.addWord("dualize",1,9,1)
b.addWord("ascot",6,10,1)
b.addWord("humaner",5,5,1)
b.addWord("warps",11,3,0)
b.printBoard()
w = b.startSearch(deck)
