__author__ = 'halley'
import random
import music21helpers as mh
import transformcell as tf
import gencell as gc

loudness = [random.randint(0,5) for i in range(0,20)]
sentiment = [random.randint(-10,10) for i in range(0,20)]
tweets = []

pitches = []
durations = []

cells = [gc.genCell(2.0,0)]
cells.append(gc.genCell(2.0, cells[-1].pits[-1]))

for i in range(0,20):
    found = False
    for j in range(0,i):
        if random.uniform(0,1) < 0.2:
            cells.append(tf.transformCell(cells[2*j], cells[-1]))
            cells.append(tf.transformCell(cells[2*j + 1], cells[-1]))
            found = True
            break
    if not found:
        cells.append(gc.genCell(2.0, cells[-1].pits[-1]))
        cells.append(gc.genCell(2.0, cells[-1].pits[-1]))

part = mh.cellsToPart(cells)
part.show()