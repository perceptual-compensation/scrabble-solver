# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 15:42:46 2016

@author: PWillis
"""
import os
import pickle
from Scrabble.Dawg import Dawg as Dawg

DICTFILE = os.path.split(__file__)[0] + "/Dictionary.txt"
DAWG = os.path.split(__file__)[0] + "/Dawg.pkl"
GADDAG = os.path.split(__file__)[0] + "/Gaddag.pkl"

if not (os.path.isfile(DAWG) and os.path.isfile(GADDAG)):
    with open(DICTFILE, "rt") as dictFile:
        wordList = dictFile.read().split()
    dawg = Dawg.makeDawg(wordList)
    with open(DAWG, "wb") as pklDawg:
        pickle.dump(dawg, pklDawg, -1)
    gaddag = Dawg.makeGaddag(wordList)
    with open(GADDAG, "wb") as pklGaddag:
        pickle.dump(gaddag, pklGaddag, -1)
else:
    with open(DAWG, "rb") as pklDawg:
        dawg = pickle.load(pklDawg)
    with open(GADDAG, "rb") as pklGaddag:
        gaddag = pickle.load(pklGaddag)

