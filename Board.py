# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 20:54:42 2016

@author: PWillis
"""
import string

class Position:
    basicTileSet = set(string.ascii_lowercase)

    def __init__(self):
        self.VTileset = Position.basicTileSet
        self.HTileset = Position.basicTileSet
        self.tile = ""

    def crossCheck(self, character, direction):
        if direction == "H":
            return character in self.VTileset
        return character in self.HTileset

    def intersect(self, characterSet, direction):
        if not characterSet.__class__ == set:
            characterSet = {characterSet}
        if direction == "H":
            self.HTileset &= characterSet
        else:
            self.VTileset &= characterSet

    def place(self, character, direction):
        if not character.__class__ == set:
            character = {character}
        if self.crossCheck(character, direction):
            self.HTileset = character
            self.VTileset = character
            self.tile = character
        else:
            raise Exception("Word incompatible.")

class Board:

    def __init__(self, nrow = 13, ncol = 13):
        self.nrow = nrow
        self.ncol = ncol
        self.boardSet = []
        for i in range(nrow * ncol):
            self.boardSet.append(Position())

    def addWord(self, word, row, col, direction):
        if direction == "H":
            if col + len(word) > self.ncol:
                raise Exception("Word too long.")
            for i, c in enumerate(word):
                self.boardSet[self.coord(row, col + i)].place(c, direction)
        else:
            if row + len(word) > self.nrow:
                raise Exception("Word too long.")
            for i, c in enumerate(word):
                self.boardSet[self.coord(row + i, col)].place(c, direction)

    def coord(self, row, col):
        if row >= self.nrow or col >= self.ncol:
            raise Exception("Coordinates out of bounds.")
        return self.ncol*row + col