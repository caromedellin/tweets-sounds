__author__ = 'halley'
from inspect import getmembers, isfunction
import celltransforms as ct
import random
import preferences as pref
import harmony as hm
import functionalhelpers as fh
import gencell as gc
import rhythmhelpers as rhy
from chunk import *


#the list of functions
transform_cell_functions = dict([(o[0], o[1]) for o in getmembers(ct) if isfunction(o[1])])

transform_cell_function_names = ['transpose', 'retrograde', 'toDouble', 'fromDouble', 'addOrnamentation', 'switchBeats']

#transform a cell
def transformCell(transformed_cell, prev_cell = gc.genBlankCell(2.0), chord_choices = [[0,2,4],[4,6,8]], best_chord = [0,2,4]):
    transform_cell_function_names = ['transpose', 'retrograde', 'toDouble', 'fromDouble', 'switchBeats']
    random.shuffle(transform_cell_function_names)
    transform_cell_function_names = ['addOrnamentation'] + transform_cell_function_names
    transform_cell_function_names.append('keepRhythm')
    function_index = -1
    while True:
        function_index += 1
        if function_index >= len(transform_cell_function_names):
            #print('dead')
            return gc.genCell(length=2.0, chord=best_chord, durs=rhy.alterRhythm(transformed_cell))#(gc.genCell(length=2.0, chord=best_chord, durs=rhy.alterRhythm(transformed_cell), cell_type=transformed_cell.ctype), 'dead')
        else:
            #print(transform_cell_function_names[function_index])
            attempting_cells = transform_cell_functions[transform_cell_function_names[function_index]](transformed_cell, prev_cell, ct.getFirstNotes(prev_cell, transformed_cell), best_chord)
            for attempting_cell in attempting_cells:
                random.shuffle(chord_choices)
                for chord in chord_choices:
                    if hm.chunkInChord(attempting_cell, chord) and pref.goodCells([prev_cell, attempting_cell]):
                        attempting_cell.chord = chord
                        return attempting_cell#(attempting_cell, transform_cell_function_names[function_index])
