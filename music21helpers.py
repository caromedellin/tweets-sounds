__author__ = 'halley'
from music21 import *
import scale as sc
import functionalhelpers as fh
from constants import *

def cellsToPart(cells, octave = 5):
    notes = []
    for cell in cells:
        degrees = cell.pits
        pits = sc.degreesToNotes(degrees, octave = 5, scale = [j + cell.key for j in scales['major']])
        durs = cell.durs
        for i in range(0, len(pits)):
            if durs[i] > 0:
                n = note.Note(pits[i])
                n.quarterLength = abs(durs[i])
                notes.append(n)
            else:
                n = note.Rest()
                n.quarterLength = abs(durs[i])
                notes.append(n)
    part = stream.Part()
    part.append(notes)
    return part

def pieceToScore(piece):
    parts = []
    for part in piece.parts:
        parts.append(cellsToPart(piece.cells[part], piece.octaves[part]))
    score = stream.Score()
    for part in parts:
        score.insert(0, part)
    return score

def showPiece(piece):
    score = pieceToScore(piece)
    score.show()

def pitsDursToPart(pits, durs):
    part = stream.Part()
    for i in range(0, len(pits)):
        if durs[i] < 0:
            rest = stream.Rest()
            rest.quarterLength = abs(durs[i])
            part.append(rest)
        else:
            if type(pits[i]) == tuple:
                chord_notes = []
                for n in pits[i]:
                    no = note.Note(n)
                    no.quarterLength = durs[i]
                    chord_notes.append(no)
                chor = chord.Chord(chord_notes)
                part.append(chor)
            else:
                n = note.Note(pits[i])
                n.quarterLength = durs[i]
                part.append(n)
    return part

