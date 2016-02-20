# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 07:54:25 2014

@author: halley
"""
from constants import *
from operator import itemgetter
import random
import probabilityhelpers as ph
import functionalhelpers as fh

#used for determining a random pitch movement
horizontalmarkov = {0:1, 1:20, 2:8, 3:2, 4:1}

#get how many chord steps (positive or negative) between pits in a cell
def getChordSteps(cell):
    chord = cell.chord
    pits = cell.pits
    steps = []
    for i in range(1, len(pits)):
        n1 = pits[i - 1]
        n2 = pits[i]
        if n1 == n2:
            steps.append(0)
        elif n1 > n2:
            step_count = 0
            while(n1 != n2):
                if n1 % 7 in [j % 7 for j in chord]:
                    step_count -= 1
                n1 -= 1
            steps.append(step_count)
        else:
            step_count = 0
            while(n1 != n2):
                if n1 % 7 in [j % 7 for j in chord]:
                    step_count += 1
                n1 += 1
            steps.append(step_count)
    return steps


#get x steps away from previous note
def stepChord(old_note, steps, chord):
    if steps == 0:
        return old_note
    else:
        new_note = old_note
        step_count = 0
        if steps > 0:
            while (step_count < steps):
                new_note += 1
                if new_note % 7 in [j % 7 for j in chord]:
                    step_count += 1
        else:
            while (step_count > steps):
                new_note -= 1
                if new_note % 7 in [j % 7 for j in chord]:
                    step_count -= 1
        return new_note

#get all chord notes within a certain distance of a starting number
def closeChordNotes(chord, start_note, max_distance):
    allnotes = fh.concat([map(lambda j: i + j, chord) for i in range(-14,14,7)])
    allnotes = filter(lambda i: abs(i - start_note) <= max_distance, allnotes)
    allnotes.sort(key=lambda i: abs(start_note - i))
    return allnotes

#whether notes clash
def matches(n1, n2):
    if n1 == None or n2 == None:
        return True
    diff = abs((n1%7) - (n2%7))
    if diff == 2 or diff == 5 or diff == 4 or diff == 3 or diff == 0 or diff == 2.5 or diff == 3.5 or diff == 5.5 or diff == 4.5:
        return True
    return False

#get closest non-clashing note in a certain direction
def getClosestMatchingNote(prev_note, match_notes, direc):
    matching = False
    note = prev_note    
    while (not matching):
        note += direc
        match = True
        for n in match_notes:
            if not matches(note, n):
                match = False
        if match:
            matching = True
            
    return note
    
#see whether notes together create one of the 4 common notes
def createsChord(notes):
    notes = filter(lambda i: i != None, notes)
    if len(set([i % 7 for i in notes])) == 0:
        return False
    chords = [[0,2,4],[4,6,1],[0,3,5], [1,3,5]]
    for chord in chords:
        if all([i == None or i % 7 in chord for i in notes]):
            return True
    return False




#convert pitches to scale degrees, given a scale
def pitchesToDegrees(pitches, scale=scales['major'], octave=5):
    degs = []
    for pitch in pitches:
        for i in range(0, len(scale)):
            if pitch%12 == (scale[i])%12:
                degs.append(i + (pitch/12 - octave)*7)
                break
            elif pitch % 12 > scale[i] and i == len(scale) - 1:
                degs.append(i + .5 + (pitch/12 - octave)*7)
            elif pitch%12 > scale[i] and pitch%12 < scale[i+1]:
                degs.append(i + .5 + (pitch/12 - octave)*7)
    return degs
    
#returns numerical notes in scale        
def notesInScale(scale=scales["major"], octave=4, startkey=0):
    return map(lambda i: i + (12*octave) + startkey, scale)
    
#get nth note of a scale
def getNote(nindex, scale=scales["major"], octave=4, startkey=0):
    return notesInScale(scale, octave, startkey)[nindex]

#given array xs, give pitches x1...xn of scale
def getNotes(nindices, octaves, scale=scales["major"], startkey=0):
    notes = []
    for note in nindices:
        notes.extend(map(lambda i: getNote(note, scale=scale, octave = i, startkey=startkey), octaves))
    return notes

#get the triad starting at scaleDeg n of scale
def triad(scaleDeg, scale=scales["major"], octave = 0):
    return [scale[scaleDeg], scale[(scaleDeg + 2) % 7] + 12*((scaleDeg + 2)/7), scale[(scaleDeg + 4) % 7] + 12*((scaleDeg + 4)/7)]

#get the interval between pitch1 and pitch2
def getInterval(pitch1, pitch2):
    return pitch2 - pitch1

#returns whether the interval between pitch1 and pitch2 is dissonant
def isDissonant(pitch1, pitch2):
    return abs(getInterval(pitch1, pitch2)) in intervals["dissonant"].values()

#get closest scale degree in triad to a given scale degree
def closestNoteDegreeInTriad(note, chord):
    allnotes = fh.concat([[i,i+2,i+4]  for i in range(-14,14,7)])
    dChords = map(lambda i: abs(note - i), allnotes)
    minindex = min(enumerate(dChords), key=itemgetter(1))[0] 
    return allnotes[minindex]

#get closest scale degree in chord to a given scale degree
def closestNoteDegreeInChord(note, chord, same = True, up_down = 0, low = None, high = None):
    allnotes = fh.concat([map(lambda j: i + j, chord) for i in range(-14,14,7)])
    if low != None:
        allnotes = filter(lambda i: i >= low, allnotes)
    if high != None:
        allnotes = filter(lambda i: i <= high, allnotes)
    tmp_allnotes = allnotes
    if up_down == 1:
        allnotes = filter(lambda i: i >= note, allnotes)
    elif up_down == -1:
         allnotes = filter(lambda i: i <= note, allnotes)
    if allnotes == [] and up_down == 1:
        allnotes = [tmp_allnotes[-1]]
    elif allnotes == [] and up_down == -1:
        allnotes = [tmp_allnotes[0]]
    dChords = map(lambda i: abs(note - i), allnotes)
    if same:
        minindex = min(enumerate(dChords), key=itemgetter(1))[0] 
        return allnotes[minindex]
    else:
        minnotsameindex = -1
        minnotsame = 1000
        for i in range(0, len(dChords)):
            if dChords[i] != 0 and dChords[i] < minnotsame:
                minnotsame = dChords[i]
                minnotsameindex = i
        return allnotes[minnotsameindex]

def closestNotesInChord(note, chord):
    all_notes = fh.concat([map(lambda j: i + j, chord) for i in range(-14,14,7)])
    dChords = [(i, abs(note - i)) for i in all_notes]
    dChords.sort(key=lambda tup:tup[1])
    return [i[0] for i in dChords]

#get notes octave
def getOctave(note):
    return (note/12)
    
#get pitchclass
def getPitchClass(note):
    return (note % 12)

#find out what index the note is in the scale
def getNoteIndex(note, scale=scales["major"], key=0):
    for i in range(0, len(scale)):
        if (note%12) == scale[i]:
            return i
    return -1
    
#get note from previous notes and intervals    
def noteAtInterval(startnote, interval, scale=scales["major"], key=0):
    nindex = getNoteIndex(startnote) #index of startnote in scale
    if nindex + interval >= len(scale):
        return (getOctave(startnote)+1)*12 + scale[(nindex + interval) % 7]
    elif nindex + interval < 0:
        return (getOctave(startnote)-1)*12 + scale[(nindex + interval) % 7]
    else:
        return startnote + scale[nindex + interval] - scale[nindex]

#get a list of intervals between notes
def getIntervals(notes, scale=[0,1,2,3,4,5,6]):
    intervals = []
    for i in range(1, len(notes)):
        ind1 = scale.index(notes[i-1]  % len(scale))
        ind2 = scale.index(notes[i]  % len(scale))
        intervals.append(ind2 - ind1)
    return intervals
    
#convert intervals to notes given intervals and startnote
def intervalsToNotes(start_note, intervals):
    notes = [start_note]
    for i in range(0, len(intervals)):
        noteNew = noteAtInterval(notes[i], intervals[i])
        if (noteNew % 12) in scales["major"]:
            notes.append(noteNew)
        else:
            print("error")
            notes.append(noteNew + random.choice([1,-1]))
    return notes
    
#convert scale degrees, octaves, scales to midi pitches
def degreesToNotes(degrees, octave = 5, scale=scales["major"]):
    notes = []
    for degree in degrees:
        if type(degree) == tuple:
            notes.append(tuple(degreesToNotes(degree, octave, scale)))
        else:
            if degree % 1.0 == 0:
                notes.append((octave+(degree/len(scale)))*12 + scale[int(degree % len(scale))])
            else:
                degree = int(degree)
                notes.append((octave+(degree/len(scale)))*12 + scale[int(degree % len(scale))] + 1)
    return notes

def degreeToNote(degree, octave = 5, scale=scales["major"]):
    if degree % 1.0 == 0:
            return((octave+(degree/7))*12 + scale[int(degree % 7)])
    else:
            degree = int(degree)
            return((octave+(degree/7))*12 + scale[int(degree % 7)] + 1)
            
def stepTranspose(pitches, steps, scale = scales["major"]):
    notes = degreesToNotes(pitches, scale=scale)
    notes = [i + steps for i in notes]
    new_degrees = pitchesToDegrees(notes, scale=scale)
    return new_degrees