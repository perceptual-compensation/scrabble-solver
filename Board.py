# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 20:54:42 2016

@author: PWillis
"""
import string, itertools
from Scrabble.Dawg import Dawg as Dawg

class Position:
    basicTileSet = set(string.ascii_lowercase)
    tileScores = {}

    def __init__(self, coords):
        self.coords = coords
        self.neighbors = [None] * 4
        self.tilesets = [Position.basicTileSet] * 2
        self.tile = ""
        self.values = (1, 1)
        self.letterScore = 1
        self.wordScore = 1
        self.crossScore = [0, 0]

    def __str__(self):
        return str(self.coords)

    def __hash__(self):
        return self.__str__().__hash__()

    def __eq__(self, other):
        return self.__str__() == other.__str__()

    def addNeighbor(self, other, direction):
        self.neighbors[direction] = other
        if other:
            other.neighbors[(direction + 2) % 4] = self

    def crossCheck(self, character, direction):
        return character in self.tilesets[not direction]

    def place(self, character, direction):
        if not self.crossCheck(character, direction):
            raise Exception("Word incompatible.")
        self.tilesets = [{character}] * 2
        self.tile = character

class Board:

    def __init__(self, nrow = 15, ncol = 15, dictionary = Dawg(), valLines = []):
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
        for line in valLines:
            place = tuple([int(i) for i in line.split("\t")[0].split(",")])
            value = tuple([int(i) for i in line.split("\t")[1:]])
            self.boardSet[place].values = value

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
                if neighbor and not neighbor.tile:
                    self.anchors.add(neighbor)
        for anchor in self.anchors:
            self.updateAnchor(anchor)

    def updateAnchor(self, anchor):
        for direction, tileset in enumerate(anchor.tilesets):
            if not anchor.neighbors[direction] \
                    or not anchor.neighbors[direction].tile:
                if not anchor.neighbors[(direction + 2) % 4] \
                        or not anchor.neighbors[(direction + 2) % 4].tile:
                    continue
            score = 0
            tiles = set()
            circumfix = ""
            pos = anchor.neighbors[direction]
            while pos and pos.tile:
                score += Position.tileScores[pos.tile]
                circumfix += pos.tile
                pos = pos.neighbors[direction]
            circumfix += "+"
            pos = anchor.neighbors[(direction + 2) % 4]
            while pos and pos.tile in dictNode.edges:
                score += Position.tileScores[pos.tile]
                circumfix += pos.tile
                pos = pos.neighbors[(direction + 2) % 4]
            
            for char in tileset:
                dictNode = self.dictionary.root.edges[char]
                pos = anchor.neighbors[direction]
                while pos and pos.tile in dictNode.edges:
                    score += Position.tileScores[pos.tile]
                    dictNode = dictNode.edges[pos.tile]
                    pos = pos.neighbors[direction]
                if (pos and pos.tile) or '+' not in dictNode.edges:
                    continue
                dictNode = dictNode.edges['+']
                pos = anchor.neighbors[(direction + 2) % 4]
                while pos and pos.tile in dictNode.edges:
                    score += Position.tileScores[pos.tile]
                    dictNode = dictNode.edges[pos.tile]
                    pos = pos.neighbors[(direction + 2) % 4]
                if (pos and pos.tile) or not dictNode.final:
                    continue
                tiles.add(char)
            print("{} {} {}".format(str(anchor),str(direction),"".join(tiles)))
            anchor.tilesets[direction] = tiles

    def printAnchors(self):
        for a in self.anchors:
            for direction, tileset in enumerate(a.tilesets):
                print("{} tileset {}: {}".format(str(a), direction, "".join(tileset)))

    def printBoard(self):
        print("   " + "  ".join([str(i) for i in range(self.ncol)[0:10]]) +
            " " + " ".join([str(i) for i in range(self.ncol)[10:]]))
        for row in range(self.nrow):
            strng = (" " if row < 10 else "") + str(row)
            for col in range(self.ncol):
                pos = self.boardSet[(row, col)]
                if pos.tile:
                    printChar = " " + pos.tile + " "
                elif pos in self.anchors:
                    printChar = " . "
                else:
                    printChar = "   "
                strng += printChar
            print(strng)

    def startSearch(self, deck, anchor = None):
        wordMap = {}
        if anchor:
            for direction in [0, 1]:
                node = self.dictionary.root
                word = ""
                self.nextTileFinder(anchor, anchor, anchor, node,
                                    deck, direction, word, wordMap)
        else:
            for a in self.anchors:
                for direction in [0, 1]:
                    node = self.dictionary.root
                    word = ""
                    self.nextTileFinder(a, a, a, node, deck, direction, word, wordMap)
        return wordMap

    def nextTileFinder(self, anchor, position, lastPosition, node,
                       deck, direction, word, wordMap):
        usableLetters = set()
        if position:
            if not position.tile:
                usableLetters = position.tilesets[not (direction % 2)] & node.edges.keys()
                if " " in deck:
                    otherLetters = set.difference(usableLetters, deck)
                    usableLetters.add(" ")
                usableLetters = set.intersection(usableLetters, deck)
            else:
                if position.tile in node.edges:
                    self.nextTileFinder(anchor, position.neighbors[direction], position,
                                        node.edges[position.tile], deck, direction,
                                        word + position.tile, wordMap)
        for letter in usableLetters:
            tempDeck = deck[:]
            tempDeck.remove(letter)
            if tempDeck is None:
                tempDeck = []
            if letter == " ":
                for otherLetter in otherLetters:
                    self.nextTileFinder(anchor, position.neighbors[direction], position,
                                        node.edges[otherLetter], tempDeck, direction,
                                        word + otherLetter, wordMap)
            else:
                self.nextTileFinder(anchor, position.neighbors[direction], position,
                                    node.edges[letter], tempDeck, direction,
                                    word + letter, wordMap)
        if not (position and position.tile):
            if "+" in node.edges:
                self.nextTileFinder(anchor, anchor.neighbors[direction + 2], anchor,
                               node.edges["+"], deck, direction + 2, word + '+', wordMap)
            if direction > 1 and node.final:
                tempWord = Dawg.daggadWord(word)
                if tempWord not in wordMap:
                    wordMap[tempWord] = set()
                wordMap[tempWord].add("{} {}".format(str(lastPosition), direction % 2))
