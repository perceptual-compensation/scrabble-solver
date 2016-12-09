# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 20:54:42 2016

@author: PWillis
"""
import string, itertools
from Scrabble.Dawg import Dawg as Dawg

class Position:
    basicTileSet = set(string.ascii_lowercase)

    def __init__(self, coords):
        self.coords = coords
        self.neighbors = set()
        self.nextPosition = [None] * 4
        self.tilesets = [Position.basicTileSet] * 2
        self.tile = ""
        self.letterScore = 1
        self.wordScore = 1

    def __str__(self):
        return str(self.coords)

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def addNeighbor(self, other, direction):
        self.nextPosition[direction] = other
        if other:
            other.nextPosition[(direction + 2) % 4] = self
            self.neighbors.add(other)
            other.neighbors.add(self)

    def crossCheck(self, character, direction):
        return character in self.tilesets[not direction]

    def intersect(self, characterSet, direction):
        try:
            self.tilesets[direction].intersection_update(characterSet)
        except:
            self.tilesets[direction].intersection_update({characterSet})

    def place(self, character, direction):
        if not self.crossCheck(character, direction):
            raise Exception("Word incompatible.")
        self.tilesets = [{character}] * 2
        self.tile = character

class Board:

    def __init__(self, nrow = 13, ncol = 13, dictionary = Dawg()):
        self.nrow = nrow
        self.ncol = ncol
        self.dictionary = dictionary
        self.boardSet = {}
        self.anchors = set()
        for r, c in itertools.product(range(nrow), range(ncol)):
            newPosition = Position((r, c))
            newPosition.addNeighbor(self.boardSet.get((r - 1, c)), 3)
            newPosition.addNeighbor(self.boardSet.get((r, c - 1)), 2)
            self.boardSet[(r, c)] = newPosition
        self.anchors.add(self.boardSet[(nrow // 2, ncol // 2)])

    def addWord(self, word, row, col, direction):
        word = word.lower()
        if row not in range(self.nrow) or col not in range(self.ncol):
            raise Exception("Position out of bounds.")
        positions = []
        if direction:
            #Vertical: direction == 1
            if row + len(word) > self.nrow:
                raise Exception("Word too long.")
            positions = [self.boardSet[i] for i in
                         itertools.product(range(row, row + len(word)), [col])]
        else:
            #Horizontal: direction == 0
            if col + len(word) > self.ncol:
                raise Exception("Word too long.")
            positions = [self.boardSet[i] for i in
                         itertools.product([row], range(col, col + len(word)))]
        if self.anchors.isdisjoint(positions):
            raise Exception("Word must be placed on an anchor.")
        for i, char in enumerate(word):
            if not positions[i].crossCheck(char, direction):
                raise Exception("Word incompatible.")
        for i, char in enumerate(word):
            positions[i].place(char, direction)
            self.anchors.discard(positions[i])
            for neighbor in positions[i].neighbors:
                if not neighbor.tile:
                    self.anchors.add(neighbor)
        for anchor in self.anchors:
            self.updateAnchor(anchor)

    def updateAnchor(self, anchor):
        tiles = [set()] * 2
        for direction, tileset in enumerate(anchor.tilesets):
            if not anchor.nextPosition[direction].tile and 
                    not anchor.nextPosition[(direction + 2) % 4].tile:
                continue
            for char in tileset:
                dictNode = self.dictionary.root.edges[char]
                pos = anchor.nextPosition[direction]
                while pos and pos.tile in dictNode.edges:
                    dictNode = dictNode.edges[pos.tile]
                    pos = pos.nextPosition[direction]
                if (pos and pos.tile) or '+' not in dictNode.edges:
                    continue
                dictNode = dictNode.edges['+']
                pos = anchor.nextPosition[(direction + 2) % 4]
                while pos and pos.tile in dictNode.edges:
                    dictNode = dictNode.edges[pos.tile]
                    pos = pos.nextPosition[(direction + 2) % 4]
                if (pos and pos.tile) or not dictNode.final:
                    continue
                tiles[direction].add(char)
        anchor.tilesets = tiles
        
