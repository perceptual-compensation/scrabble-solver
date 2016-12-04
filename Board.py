# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 20:54:42 2016

@author: PWillis
"""
import string, itertools

class Position:
    basicTileSet = set(string.ascii_lowercase)

    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.VTileset = Position.basicTileSet
        self.HTileset = Position.basicTileSet
        self.tile = ""
        self.anchor = False

    def crossCheck(self, character, direction):
        if direction == "H":
            return character in self.VTileset
        return character in self.HTileset

    def intersect(self, characterSet, direction):
        if characterSet.__class__ != set:
            characterSet = {characterSet}
        if direction == "H":
            self.HTileset &= characterSet
        else:
            self.VTileset &= characterSet

    def place(self, character, direction):
        if character.__class__ == set:
            if len(character) != 1:
                raise Exception("Can't place this set.")
            else:
                character = character.pop()
        if self.crossCheck(character, direction):
            self.HTileset = {character}
            self.VTileset = {character}
            self.tile = character
            self.anchor = False
        else:
            raise Exception("Word incompatible.")

class Board:

    def __init__(self, nrow = 13, ncol = 13):
        self.nrow = nrow
        self.ncol = ncol
        self.boardSet = {}
        self.anchors = []
        for i in itertools.product(range(nrow), range(ncol)):
            self.boardSet[i] = Position(i)

    def addWord(self, word, row, col, direction):
        if direction == "H":
            if col + len(word) > self.ncol:
                raise Exception("Word too long.")
            for i, c in enumerate(word):
                self.boardSet[(row, col + i)].place(c, direction)
        else:
            if row + len(word) > self.nrow:
                raise Exception("Word too long.")
            for i, c in enumerate(word):
                self.boardSet[(row + i, col)].place(c, direction)
