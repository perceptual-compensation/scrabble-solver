# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 20:54:42 2016

@author: PWillis
"""
import string, itertools
from Scrabble.Dawg import Dawg as Dawg

class Position:
    basicLetterSet = set(string.ascii_lowercase)
    tileScores = {'a':1, 'b':3, 'c':3, 'd':2, 'e':1,
                  'f':4, 'g':2, 'h':4, 'i':1, 'j':8,
                  'k':5, 'l':1, 'm':3, 'n':1, 'o':1,
                  'p':3, 'q':10, 'r':1, 's':1, 't':1,
                  'u':1, 'v':4, 'w':4, 'x':8, 'y':4,
                  'z':10, ' ':0}

    def __init__(self, coords):
        self.coords = coords
        self.neighbors = [None] * 4
        self.lettersets = [Position.basicLetterSet] * 2
        self.tile = ""
        self.letter = ""
        self.values = (1, 1)
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

    def crossCheck(self, letter, direction):
        return letter in self.lettersets[not direction]

    def place(self, tile, direction, letter = ""):
        if not self.crossCheck(tile, direction):
            raise Exception("Word incompatible.")
        if tile != " ":
            letter = tile
        self.lettersets = [{letter}] * 2
        self.tile = tile
        self.letter = letter

class Board:

    def __init__(self, nrow = 15, ncol = 15, 
                 dictionary = Dawg(), boardValueLines = [], tileValueLines = []):
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
        for line in boardValueLines:
            place = tuple([int(i) for i in line.split("\t")[0].split(",")])
            value = tuple([int(i) for i in line.split("\t")[1:]])
            self.boardSet[place].values = value
        if tileValueLines:
            Position.tileScores = {}
            for line in tileValueLines:
                Position.tileScores[line.split("\t")[0].lower()] = \
                                    int(line.split("\t")[1])

    def addWord(self, word, row, col, direction, blanks = []):
        word = word.lower()
        if word.count(" ") > len(blanks):
            raise Exception("Not all blanks in word have been specified.")
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
        blankCount = 0
        for i, tile in enumerate(word):
            if tile == " ":
                if not positions[i].crossCheck(blanks[blankCount], direction):
                    raise Exception("Word incompatible.")
                blankCount += 1
            else:
                if not positions[i].crossCheck(tile, direction):
                    raise Exception("Word incompatible.")
        blankCount = 0
        for i, tile in enumerate(word):
            if tile == " ":
                positions[i].place(tile, direction, blanks[blankCount])
                blankCount += 1
            else:
                positions[i].place(tile, direction)
            self.anchors.discard(positions[i])
            for neighbor in positions[i].neighbors:
                if neighbor and not neighbor.tile:
                    self.anchors.add(neighbor)
        for anchor in self.anchors:
            self.updateAnchor(anchor)

    def updateAnchor(self, anchor):
        for direction, letterset in enumerate(anchor.lettersets):
            if not anchor.neighbors[direction] \
                    or not anchor.neighbors[direction].tile:
                if not anchor.neighbors[(direction + 2) % 4] \
                        or not anchor.neighbors[(direction + 2) % 4].tile:
                    continue
            score = 0
            letters = set()
            circumfix = ""
            pos = anchor.neighbors[direction]
            while pos and pos.tile:
                score += Position.tileScores[pos.tile]
                circumfix += pos.letter
                pos = pos.neighbors[direction]
            circumfix += "+"
            pos = anchor.neighbors[(direction + 2) % 4]
            while pos and pos.tile:
                score += Position.tileScores[pos.tile]
                circumfix += pos.letter
                pos = pos.neighbors[(direction + 2) % 4]
            for l in letterset:
                dictNode = self.dictionary.root.edges[l]
                for char in circumfix:
                    if char in dictNode.edges:
                        dictNode = dictNode.edges[char]
                    else:
                        continue
                if not dictNode.final:
                    continue
                letters.add(l)
            anchor.lettersets[direction] = letters
            anchor.crossScore[direction] = score
        
#            for char in letterset:
#                dictNode = self.dictionary.root.edges[char]
#                pos = anchor.neighbors[direction]
#                while pos and pos.tile in dictNode.edges:
#                    score += Position.tileScores[pos.tile]
#                    dictNode = dictNode.edges[pos.tile]
#                    pos = pos.neighbors[direction]
#                if (pos and pos.tile) or '+' not in dictNode.edges:
#                    continue
#                dictNode = dictNode.edges['+']
#                pos = anchor.neighbors[(direction + 2) % 4]
#                while pos and pos.tile in dictNode.edges:
#                    score += Position.tileScores[pos.tile]
#                    dictNode = dictNode.edges[pos.tile]
#                    pos = pos.neighbors[(direction + 2) % 4]
#                if (pos and pos.tile) or not dictNode.final:
#                    continue
#                letters.add(char)
#            print("{} {} {}".format(str(anchor),str(direction),"".join(letters)))
#            anchor.lettersets[direction] = letters

    def printAnchors(self):
        for a in self.anchors:
            for direction, letterset in enumerate(a.lettersets):
                print("{} letterset {}: {}".format(str(a), direction, "".join(letterset)))

    def printBoard(self):
        print("   " + "  ".join([str(i) for i in range(self.ncol)[0:10]]) +
            " " + " ".join([str(i) for i in range(self.ncol)[10:]]))
        for row in range(self.nrow):
            strng = (" " if row < 10 else "") + str(row)
            for col in range(self.ncol):
                pos = self.boardSet[(row, col)]
                if pos.tile:
                    printChar = " " + pos.tile + " "
                    if pos.tile == " ":
                        printChar = " " + pos.letter.upper() + " "
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
                usableLetters = position.lettersets[not (direction % 2)] & node.edges.keys()
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
