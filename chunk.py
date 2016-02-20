# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 20:11:47 2015

@author: halley
"""
import functionalhelpers as fh
import rhythmhelpers as rhy







#A chunk of music
class Chunk():
    def setKey(self, key):
        self.key = key
        if self.sub_chunks != None:
            for sub_chunk in self.sub_chunks:
                sub_chunk.setKey(key)
            for i in range(0, len(self.cells)):
                self.cells[i].key = key
    def resetBeatPitsAndDurs(self):
        self.beat_durs = []
        new_note = True
        for note in self.durs:
            if new_note:
                self.beat_durs.append([note])
                if (note % 1) != 0:
                    new_note = False
            else:
                self.beat_durs[-1].append(note)
                if sum(self.beat_durs[-1]) % 1 == 0:
                    new_note = True
        #print('beat durs' + str(self.beat_durs) + ' pits ' + str(self.pits))
        self.beat_pits = fh.mapStructure(self.beat_durs, self.pits)
    def setLength(self):
        exact_length = sum(map(abs, self.durs))
        length = 0.125
        while True:
            if abs(length - exact_length) < 0.001:
                self.length = length
                return
            length += 0.125
    def appendPitsDurs(self, pits, durs):
        self.pits += pits
        self.durs += durs

        self.resetBeatPitsAndDurs()

    def setPitsDurs(self, pits, durs):
        self.pits = pits
        self.durs = durs

        self.resetBeatPitsAndDurs()

    def __init__(self, pits = [], durs = [], chord = [], sub_chunks = None, key = 0, name='', scale = [0,2,4,5,7,9,11], dynamics = 'mf'):
        self.sub_chunks = sub_chunks
        self.name = name
        self.chord = chord
        #find depth
        if sub_chunks == None or sub_chunks == []:
            self.depth = 0
        else:
            self.depth = sub_chunks[0].depth

        self.key = key
        self.setKey(key)
        self.scale = scale
        #find pits/durs
        if pits == [] and self.depth > 0:
            pits = fh.concat([i.pits for i in self.cells])
            durs = fh.concat([i.durs for i in self.cells])
        self.pits = pits
        self.durs = durs

        #get ctype - basically only useful for cells
        self.ctype = self.getCtype(self.pits)

        #get beat rhythms and pitches
        self.beat_durs = []
        self.beat_pits = []
        self.resetBeatPitsAndDurs()
        self.length = []
        self.setLength()
    def mapAllPits(self, f):
        if self.depth == 0:
            self.setPitsDurs(self, f(self.pits), self.durs)
        else:
            for sub_chunk in self.sub_chunks:
                sub_chunk.mapAllPits(f)
    def getCells(self, chunk):
        if chunk.depth == 0:
            return [chunk]
        else:
            return fh.concat([self.getCells(i) for i in chunk.sub_chunks])
    def getCtype(self, pits):
        intervals = [pits[i] - pits[i - 1] for i in range(1, len(pits))]
        if all([i in range(-1,1) for i in intervals]):
            return 'scalewise'
        chords = [[i + j for i in [0,2,4]] for j in range(0,7)]
        for chord in chords:
            if all([i % 7 in [j % 7 for j in chord] for i in pits]):
                return 'chordal'
        return 'other'
