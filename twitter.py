__author__ = 'halley'
import random
import music21helpers as mh
import transformcell as tf
import gencell as gc
import accompaniment as acc
from music21 import *
import copy
import json
import sys


def getLoudness(loudness):
    if i < 0.1:
        return 'p'
    elif i < 0.25:
        return 'mp'
    elif i < 0.5:
        return 'mf'
    elif i > 0.75:
        return 'f'
    else:
        return 'fff'

f = open(sys.argv[1] + '.json', 'r+')
data = json.load(f)
sentiment = [i['sentiment'] for i in data]
similarities = [i['similarity'] for i in data]
loudness = [i['loudness'] for i in data]
loudness = [i + (1.0-max(loudness)) for i in loudness]
loudness = [getLoudness(i) for i in loudness]

hashTagFreq = [i['hashtags'] for i in data]

melody_cells = [gc.genCell(2.0,0)]
melody_cells.append(gc.genCell(2.0, melody_cells[-1].pits[-1]))

bass_cells = []

def getScale(sentiment):
    if sentiment == 0:
        return [0,2,4,6,8,10]
    elif sentiment <= 0:
        return [0,2,3,5,7,8,10]
    else:
        return [0,2,4,5,7,9,11]


for i in range(0,len(data)):
    sims = similarities[i][:i]
    if len(sims) == 0 or max(sims) < 0.2:
        print('in')
        if random.uniform(0,1) < 0.5:
            melody_cells.append(gc.genCell(2.0, melody_cells[-1].pits[-1]))
            melody_cells.append(gc.genCell(2.0, melody_cells[-1].pits[-1]))
        else:
            melody_cells.append(gc.genCell(2.0, melody_cells[-1].pits[-1]))
            melody_cells.append(tf.transformCell(melody_cells[-1], melody_cells[-1]))
    else:
        most_similar = filter(lambda j: sims[j] == max(sims), range(0,i))[0]
        if random.uniform(0,1) < 0.4:
            melody_cells.append(tf.transformCell(melody_cells[2*most_similar+2], melody_cells[-1]))
            melody_cells.append(copy.deepcopy(melody_cells[2*most_similar+3]))
        elif random.uniform(0,1) < 0.8:
            melody_cells.append(copy.deepcopy(melody_cells[2*most_similar+2]))
            melody_cells.append(tf.transformCell(melody_cells[2*most_similar + 3], melody_cells[-1]))
        else:
            melody_cells.append(copy.deepcopy(melody_cells[2*most_similar+2]))
            melody_cells.append(copy.deepcopy(melody_cells[2*most_similar+3]))
    bass_cells.extend(acc.getBass(melody_cells[-2:], hashTagFreq[i]))

    melody_cells[-2].scale = getScale(sentiment[i])
    melody_cells[-1].scale = getScale(sentiment[i])
    bass_cells[-2].scale = getScale(sentiment[i])
    bass_cells[-1].scale = getScale(sentiment[i])


melody_cells = melody_cells[2:]

part1 = mh.cellsToPart(melody_cells)
part1.insert(0, instrument.fromString('Flute'))

for i in range(0, len(loudness)):
    part1.insert(i*4.0, dynamics.Dynamic(loudness[i]))

part2 = mh.cellsToPart(bass_cells, octave=4)
part2.insert(0, instrument.fromString('Violoncello'))

s = stream.Score()
s.insert(0, part1)
s.insert(0, part2)

s.show()