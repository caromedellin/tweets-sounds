__author__ = 'halley'
import scale as sc
from chunk import *
import gencell as gc
import random

def getFirstNotes(prev_cell, old_cell):
    ppit = prev_cell.pits[-1]
    if (ppit % 7) in (i % 7 for i in prev_cell.chord):
        return [ppit - 1, ppit + 1, ppit]
    else:
        if prev_cell.pits < 14 and random.uniform(0,1) < 0.4 or prev_cell.pits[-1] < 0:
            return list(set([ppit + 1, ppit - 1, old_cell.pits[-1], ppit + 2, ppit - 2, ppit + 3, ppit - 3]))
        else:
            return list(set([ppit - 1, ppit + 1, old_cell.pits[-1], ppit - 2, ppit + 2, ppit - 3, ppit + 3]))

def transposes(first_notes, intervals):
    new_cells = []
    for first_note in first_notes:
            new_pits = [first_note]
            for interval in intervals:
                new_pits.append(interval + new_pits[-1])
            new_cells.append(new_pits)
    return new_cells

#transpose cell
def transpose(old_cell, prev_cell, first_notes, chord = [0,2,4]):
    new_cells = []
    if old_cell.ctype == 'CHORDAL':
        steps = sc.getChordSteps(old_cell)
        if prev_cell.ends_on_chord:
            first_notes = sc.closeChordNotes(chord, start_note=prev_cell.pits[-1], max_distance=4)
        else:
            first_notes = sc.closeChordNotes(chord, start_note=prev_cell.pits[-1], max_distance=1)
        for first_note in first_notes:
            new_pits = [first_note]
            for step in steps:
                new_pits.append(sc.stepChord(new_pits[-1], step, chord))
            new_cells.append(Chunk(new_pits, old_cell.durs, chord=chord, key=prev_cell.key))
    else:
        intervals = [old_cell.pits[i] - old_cell.pits[i - 1] for i in range(1, len(old_cell.pits))]
        new_pits = transposes(first_notes, intervals)
        for pits in new_pits:
            new_cells.append(Chunk(pits = pits, durs = old_cell.durs, chord=[]))
    return new_cells


#add double notes
def toDouble(old_cell, prev_cell, first_notes = [], chord=[0,2,4]):
    pits = old_cell.pits
    durs = old_cell.durs
    new_cells = []
    if 1.0 in durs:
        new_durs = []
        new_pits = []
        for i in range(0, len(durs)):
            if durs[i] == 1.0:
                new_durs.extend([0.5,0.5])
                new_pits.extend([pits[i], pits[i]])
            else:
                new_durs.append(durs[i])
                new_pits.append(pits[i])
        new_intervals = sc.getIntervals(new_pits)
        new_pits = transposes(first_notes, new_intervals)
        for pits in new_pits:
            new_cells.append((Chunk(pits, new_durs, chord=[], key=prev_cell.key)))
    elif 2.0 in durs:
        new_intervals = [[0],[-1],[1]]
        new_durs = [1.0, 1.0]
        new_pits = []
        for new_interval in new_intervals:
            new_pits.extend(transposes(first_notes, new_interval))
        for pits in new_pits:
            new_cells.append(Chunk(pits = pits, durs = new_durs, chord = []))
    return new_cells

#remove double notes
def fromDouble(old_cell, prev_cell, first_notes = [], chord=[0,2,4]):
    new_cells = []
    new_pits = []
    new_durs = []
    new_intervals = []
    for i in range(0, len(old_cell.beat_pits)):
        if len(set(old_cell.beat_pits[i])) == 1 and all([j > 0 for j in old_cell.beat_durs[i]]):
            new_pits.append(old_cell.beat_pits[i][0])
            new_durs.append(sum(old_cell.beat_durs[i]))
        else:
            new_pits.extend(old_cell.beat_pits[i])
            new_durs.extend(old_cell.beat_durs[i])
    new_pits = transposes(first_notes, sc.getIntervals(new_pits))
    for pits in new_pits:
        new_cells.append(Chunk(pits=pits, durs=new_durs, chord=[]))
    else:
        return []


#create an inversion
def inversion(old_cell, prev_cell, first_notes = [], chord=[0,2,4]):
    intervals = [old_cell.pits[i] - old_cell.pits[i - 1] for i in range(1, len(old_cell.pits))]
    intervals = [i * -1 for i in intervals]
    new_pits = transposes(first_notes, intervals)
    new_cells = []
    for pits in new_pits:
        new_cells.append(Chunk(pits=pits, durs=old_cell.durs, chord=[], key=prev_cell.key))
    return new_cells

def keepRhythm(old_cell, prev_cell, first_notes, chord=[0,2,4]):
    first_notes = ([old_cell.pits[-1] + i for i in [0,-1,1]])
    first_notes.extend([prev_cell.pits[-1] + i for i in range(-4,4)])
    new_cells = []
    for first_note in first_notes:
        for i in range(0,4):
            durs = rhy.alterRhythm(old_cell)
            #print(durs)
            new_cells.append(gc.genCell(length=old_cell.length, first_note=first_note, chord=chord, durs=durs, cell_type = old_cell.ctype))
    return new_cells


def addOrnamentation(old_cell, prev_cell, first_notes, chord=[0,2,4]):
    new_cells = []
    beat_durs = old_cell.beat_durs
    beat_pits = old_cell.beat_pits
    new_pits = []
    new_durs = []
    for i in range(0, len(beat_durs)):
        if beat_durs[i] == [1.0]:
            opit = beat_pits[i][0]
            new_durs.extend([0.25, 0.25, 0.25, 0.25])
            new_pits.extend([opit, opit + 1, opit - 1, opit])
        else:
            new_durs.extend(beat_durs[i])
            new_pits.extend(beat_pits[i])
    intervals = sc.getIntervals(new_pits)
    new_pits = transposes(first_notes, intervals)
    for pits in new_pits:
        new_cells.append(Chunk(pits=pits, durs=new_durs, chord=[]))
    if new_durs == old_cell.durs:
        return []
    return new_cells

def switchBeats(old_cell, prev_cell, first_notes, chord=[0,2,4]):
    if len(old_cell.beat_pits) < 2:
        return []
    new_cells = []
    new_pits = old_cell.beat_pits[1] + old_cell.beat_pits[0]
    new_durs = old_cell.beat_durs[1] + old_cell.beat_durs[0]
    new_intervals = sc.getIntervals(new_pits)
    new_pits = transposes(first_notes, new_intervals)
    for pits in new_pits:
        new_cells.append(Chunk(pits=pits, durs=new_durs, chord=[]))
    return new_cells

def retrograde(old_cell, prev_cell, first_notes, chord=[0,2,4]):
    '''
    retrograde pitches, not duration
    retrograde pitches and duration
    retrograde first beat
    retrograde second beat
	'''
    if len(old_cell.durs) == 1:
        return []
    new_cells = []
    opits = old_cell.pits
    new_intervals = sc.getIntervals(opits[::-1])
    new_pits = transposes(first_notes, new_intervals)
    for pits in new_pits:
        new_cells.append(Chunk(pits, old_cell.durs, []))
        new_cells.append(Chunk(pits, old_cell.durs[::-1], []))
    if len(old_cell.beat_pits) == 1:
        return new_cells

    new_pits = old_cell.beat_pits[0][::-1] + old_cell.beat_pits[1]
    new_intervals = sc.getIntervals(new_pits)
    new_pits = transposes(first_notes, new_intervals)
    for pits in new_pits:
        new_cells.append(Chunk(pits, old_cell.durs, []))
    new_pits = old_cell.beat_pits[0] + old_cell.beat_pits[1][::-1]
    new_intervals = sc.getIntervals(new_pits)
    new_pits = transposes(first_notes, new_intervals)
    for pits in new_pits:
        new_cells.append(Chunk(pits, old_cell.durs, []))
    random.shuffle(new_cells)
    return new_cells