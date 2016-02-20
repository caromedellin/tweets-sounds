__author__ = 'halley'
from chunk import *
import scale as sc
import harmony as hm
import gencell as gc
import pitchhelpers as pth
import random


def genHalfNotes(main_passage):
    half_notes = []
    for cell in main_passage:
        if cell.chord == []:
            half_notes.append(Chunk(pits=[cell.pits[0]],durs=[2.0]))
        else:
            half_notes.append(Chunk(pits=[random.choice(cell.chord)], durs = [2.0]))
    return half_notes

#create quarter note accompaniment
def genQuarters(main_cells):
    quarter_cells = []
    prev_note = -3
    pre_prev_note = -2
    for main_cell in main_cells:
        main_pits = [i[0] for i in main_cell.beat_pits]
        if len(main_pits) == 1:
            main_pits.append(None) #we have a "Free" note
        if main_cell.chord == None or main_cell.chord == []:
            quarter_cells.append(gc.genBlankCell(2.0))
        else:
            pits = []
            for main_pit in main_pits:
                if main_pit == None:
                    if pre_prev_note == prev_note:
                        pits.append(sc.closestNoteDegreeInChord(prev_note + random.choice([-2,2]), main_cell.chord))
                    else:
                        pits.append(sc.closestNoteDegreeInChord(prev_note, main_cell.chord))
                else:
                    closest_chord_notes = sc.closestNotesInChord(prev_note + random.choice([-2,2]), main_cell.chord)
                    closest_chord_notes = filter(lambda i: i > -7, closest_chord_notes)
                    for chord_note in closest_chord_notes:
                        if hm.matches(chord_note, main_pit):
                            pits.append(chord_note)
                            break
                pre_prev_note = prev_note
                prev_note = pits[-1]
            durs = [1.0,1.0]
            quarter_cells.append(Chunk(pits=pits, durs=durs, chord=main_cell.chord, key = main_cell.key))
        prev_note = quarter_cells[-1].pits[-1]
    return quarter_cells

#get alberti eighths for a given chord, and matching pitches and durations
def getAlbertiEighths(prog, pitches, durs, inversion = False):
    tot_durs = [sum(durs[:i]) for i in range(0, len(durs))]
    eighths = []
    for i in range(0, 4):
        found = False
        for j in range(0, len(tot_durs)):
            if tot_durs[j] == i/2.0:
                eighths.append(pitches[j])
                found = True
        if found == False:
            eighths.append(None)
    #randomly choose among alberti patterns
    if inversion:
        alberti_pats =  [[1,0,2,0], [1,0,1,2], [1,2,1,0], [1,0,1,0]]
    else:
        alberti_pats = [[0,1,2,1], [0,2,1,2], [0,1,0,2], [0,2,0,1], [0,1,0,1], [0,2,0,2]]
    for pat in alberti_pats: #find one that matches
        if all(map(lambda i: hm.matches(eighths[i], prog[pat[i]]), range(0,4))):
            return [prog[j] for j in pat]
    return [-36,-36,-36,-36]

#create alberti eighth accompaniment
def genAlbertiEighths(main_cells, leading_eighths = True):
    prev_note = 0
    cells = []
    for k in range(0, len(main_cells)): #loop through all cells
        main_cell = main_cells[k]
        if main_cell.chord == None or main_cell.chord == []:
            if leading_eighths == False: #if we are coming to a close
                new_pits = []
                for pit in main_cell.pits:
                    new_pits.append(pth.getClosestPCDegree(prev_note, pit, low = -5, high = 14))
                    prev_note = new_pits[-1]
                cells.append(Chunk(pits = new_pits, durs = main_cell.durs, key=main_cell.key))
            else: #if we want eighths
                main_pitches = main_cell.pits
                main_durs = main_cell.durs
                pits = []
                tot_durs = [sum(main_durs[:i]) for i in range(0, len(main_durs))]
                eighths = []
                for i in range(0, 4):
                    found = False
                    for j in range(0, len(tot_durs)):
                        if tot_durs[j] == i/2.0:
                            eighths.append(main_pitches[j])
                            found = True
                    if found == False:
                        eighths.append(None)
                if eighths[1] == None and eighths[2] == None and eighths[3] == None:
                    if main_pitches[0] % 7 == 1 or main_pitches[0] % 7 == 6: #if we're dealing with a dominant chord
                        first_note = (pth.getClosestPC(prev_note, 4))
                    else:
                        first_note = (pth.getClosestPC(prev_note, 0))
                    pat = random.choice([[0,-1,-2,-3], [0,-1,-2,-1]])
                    pits = [first_note + i for i in pat]
                else:
                    if hm.matches(eighths[0], 0):
                        pits.append(pth.getClosestPCDegree(prev_note, 0))
                    elif hm.matches(eighths[0], 4):
                        pits.append(pth.getClosestPCDegree(prev_note, 7))
                    else:
                        print('error')
                    prev_note = pits[-1]
                    for note in eighths[1:]: #run through all of the possibilities of the notes
                        if hm.inChord(note, [0,2,4]):
                            pits.append(sc.closestNoteDegreeInChord(prev_note, [0,2,4], same=False))
                        elif hm.inChord(note, [4,6,8]):
                            pits.append(sc.closestNoteDegreeInChord(prev_note, [4,8], same=False))
                        elif note == None:
                            pits.append(prev_note + random.choice([-1,1]))
                        else:
                            pits.append(pth.getClosestPCDegree(prev_note, note))
                            prev_note = pits[-1]
                cells.append(Chunk(pits=pits, durs=[0.5,0.5,0.5,0.5], key = main_cell.key))
        else: #if there is a chord
            inversion = False
            chord = main_cell.chord
            if chord == [1,3,5] or chord == [-2,0,2] or chord == [5,7,9]:
                inversion = True
            if k > 0:
                if main_cells[k - 1].chord == [0,2,4] and chord == [0,2,4]:
                    inversion = True
            '''if diff(main_cell.beat_pits[0], chord[1] == octave and diff(cells[-1].pits[-1], main_cells[k].beat_pits[0] == octave:
                inversion = False
            '''
            eighths = getAlbertiEighths(chord, main_cell.pits, main_cell.durs, inversion=inversion)
            #if isDiminished(eighths[0],cells[-1].pits[-1]:
            #   choose different end for cells[-1]
            closest_eighths = []
            for i in range(0, len(eighths)):
                closest_eighths.append(pth.getClosestPC(prev_note, eighths[i]))
                prev_note = closest_eighths[-1]
            cells.append(Chunk(pits = closest_eighths, durs = [0.5,0.5,0.5,0.5], chord=chord, key=main_cell.key))
    return cells


def getBass(cells, hashFreq):
    if hashFreq == 0:
        return genHalfNotes(cells)
    elif hashFreq == 1:
        return genQuarters(cells)
    else:
        return genAlbertiEighths(cells)