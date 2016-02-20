__author__ = 'halley'
from constants import *
from chunk import *
import copy
import probabilityhelpers as ph

def inChord(note, chord):
    if chord == []:
        return True
    if note == None:
        return True
    else:
        return (note % 7) in [i%7 for i in chord]


#check if an entire chunk matches
def chunkMatches(chunk1, chunk2):
    if chunk1.sub_chunks == [] or chunk1.sub_chunks == None:
        if len(chunk1.pits) != len(chunk1.durs) or len(chunk2.pits) != len(chunk2.durs):
            return False
        tot_durs1 = [sum(chunk1.durs[:i]) for i in range(0, len(chunk1.durs))]
        pits1 = chunk1.pits
        tot_durs2 = [sum(chunk2.durs[:i]) for i in range(0, len(chunk2.durs))]
        pits2 = chunk2.pits
        j_index = 0
        for i in range(0, len(tot_durs1)):
            for j in range(j_index, len(tot_durs2)):
                if tot_durs1[i] == tot_durs2[j]:
                    if not matches(pits1[i], pits2[j]):
                        return False
                    j_index = j
        return True
    else:
        print('error - larger chunks not implemented yet')

#check if a chunk is in a chord
def chunkInChord(chunk, chord):
    pits = chunk.pits
    #print(pits)
    if inChord(pits[0], chord):
        for i in range(1, len(pits)):
            if abs(pits[i] - pits[i - 1]) > 1:
                if not (inChord(pits[i], chord) and inChord(pits[i - 1], chord)):
                    return False
        return True
    else:
        return False

#get closest note in chord above note
def getClosestAbove(note, chord):
    #print('note ' + str(note) + 'chord ' + str(chord))
    i = 1
    while (not inChord(note + i, chord)):
        i += 1
    return note + i

#get closest note in chord below note
def getClosestBelow(note, chord):
    #print('note ' + str(note) + 'chord ' + str(chord))
    i = 1
    while (not inChord(note - i, chord)):
        i += 1
    return note - i

def matches(n1, n2):
    #print('matching ' + str(n1) + ' and ' + str(n2))
    if n1 == None or n2 == None:
        return True
    diff = abs((n1%7) - (n2%7))
    if diff == 2 or diff == 5 or diff == 4 or diff == 0 or diff == 3:
        return True
    return False


#find what chord matches a given cell
def getChord(cell):
    pits = cell.pits
    diffs = [abs(pits[i] - pits[i - 1]) for i in range(1, len(pits))]
    important = []
    important.append(pits[0])
    for i in range(0, len(diffs)):
        if diffs[i] > 2:
            important.append(pits[i])
            important.append(pits[i + 1])
    return (-7,-5,-3)

#transpose chunk so that it fits a new chord
def transposeToChord(chunk, chord, prev_note = 0):
    if chunk.depth == 0:
        #get closest above with chord
        distance = getClosestAbove(chunk.pits[0], chord) - chunk.pits[0]
        new_pits = [i + distance for i in chunk.pits]
        chunk_above = Chunk(None, new_pits, chunk.durs, chunk.ctype)

        distance = chunk.pits[0] - getClosestBelow(chunk.pits[0], chord)
        new_pits = [i - distance for i in chunk.pits]
        chunk_below = Chunk(None, new_pits, chunk.durs, chunk.ctype)

        new_chunks = [chunk_below, chunk_above]
        if chunkInChord(chunk, chord):
            new_chunks.append(chunk)
        return new_chunks
    elif chunk.depth == 1:
        distance = getClosestAbove(chunk.pits[0], chord) - chunk.pits[0]
        chunk_above = copy.deepcopy(chunk)
        for i in range(0, len(chunk_above.sub_chunks)):
            chunk_above.sub_chunks[i].setPitsDurs([j + distance for j in chunk_above.sub_chunks[i].pits], chunk_above.sub_chunks[i].durs)

        distance = getClosestBelow(chunk.pits[0], chord) - chunk.pits[0]
        chunk_below = copy.deepcopy(chunk)
        for i in range(0, len(chunk_below.sub_chunks)):
            chunk_below.sub_chunks[i].setPitsDurs([j + distance for j in chunk_below.sub_chunks[i].pits], chunk_below.sub_chunks[i].durs)
        new_chunks = [chunk_above, chunk_below]
        if inChord(chunk.pits[0], chord):
            new_chunks.append(chunk)
        return new_chunks
    else:
        return [chunk]

#convert from root of chord to chord
def rootToChord(base):
    return [base, base + 2, base + 4]

#convert from chord to root
def chordToRoot(chord):
    return chord[0]

#get all pos chords fitting between prev_chord and end_Chord
def getPosChords(prev_chord = None, end_chord = None):
    if prev_chord != None:
        pos_prev_chord = chord_movements[chordToRoot(prev_chord)]
    else:
        pos_prev_chord = range(0,6)
    if end_chord != None:
        pos_prev_chord = filter(lambda i: end_chord in chord_movements[i], pos_prev_chord)
    return [rootToChord(root) for root in pos_prev_chord]

#get all pos chord roots fitting between prev_chord and end_Chord
def getPosChordRoots(prev_chord = None, end_chord = None):
    if prev_chord != None:
        pos_prev_chord = chord_movements[chordToRoot(prev_chord)]
    else:
        pos_prev_chord = range(0,6)
    if end_chord != None:
        pos_prev_chord = filter(lambda i: end_chord in chord_movements[i], pos_prev_chord)
    return pos_prev_chord

chord_prob_dict = {0:0.5, 1:0.1, 2:0.01, 3:0.2, 4:0.3, 5:0.1, 6:0.05}

def getHighestProbChord(prev_chord, end_chord):
    roots = getPosChordRoots(prev_chord, end_chord)
    pdict = chord_prob_dict.values()
    pdict = dict(filter(lambda i: i[0] in roots, pdict))
    return rootToChord(ph.highestProb(pdict))
