__author__ = 'halley'
import functionalhelpers as fh
import harmony as hm

#test if a single cell = good
def goodCell(cell):
    if len(cell.durs) != len(cell.pits):
        return False
    if len(cell.durs) == 1:
        return True
    pits = cell.pits
    durs = cell.durs
    pit_diffs = [abs(pits[i] - pits[i - 1]) for i in range(1, len(pits))]
    #no three in a row
    for i in range(2, len(pits)):
        if pits[i] == pits[i - 1] and pits[i - 2] == pits[i]:
            return False
    for i in range(1, len(pits)):
        if durs[i] == 0.25 and durs[i - 1] == 0.25 and pits[i] == pits[i - 1]:
            return False
    #no jumps bigger than 4
    if max(pit_diffs) > 4:
        return False
    #no notes lower than -3
    if min(pits) < -3:
        return False
    if max(pits) > 20:
        return False
    #don't hang leading tone
    if pits[-1] % 7 == 6:
        return False
    return True


def goodCells(cells, melody = True):
    for cell in cells:
        if len(cell.pits) != len(cell.durs):
            return False

    if not all([len(i.pits) == len(i.durs) for i in cells]):
        return False
    pits = fh.concat([j.pits for j in cells])
    durs = fh.concat([j.durs for j in cells])
    beat_pits = fh.concat([j.beat_pits for j in cells])
    beat_durs = fh.concat([j.beat_durs for j in cells])
    #no more than 4 half notes
    if durs.count(2.0) > 4:
        return False

    #no leaping from non-tone chord
    if not hm.inChord(cells[0].pits[-1], cells[0].chord) and abs(cells[0].pits[-1] - cells[1].pits[0]) > 1:
        return False
    pit_diffs = [abs(pits[i] - pits[i - 1]) for i in range(1, len(pits))]
    for i in range(1, len(pits)):
        #no jumps of a seventh
        if abs(pits[i] - pits[i - 1]) == 6:
            return False
        #no tritones
        if (pits[i] % 7) == 3 and (pits[i - 1] % 7) == 6 or  (pits[i] % 7) == 6 and (pits[i - 1] % 7) == 3:
            return False
    #no three in a row
    for i in range(2, len(pits)):
        if pits[i] == pits[i - 1] and pits[i - 2] == pits[i]:
            return False
    #no jumps more than an octave
    if max(pit_diffs) > 7:
        return False
    #no two arpeggiated cells
    for i in range(0, len(beat_pits) - 3):
        if max(beat_pits[i]) - min(beat_pits[i]) > 4:
            if max(beat_pits[i + 3]) - min(beat_pits[i + 3]) > 4 or max(beat_pits[i + 1]) - min(beat_pits[i + 1]) > 4 or max(beat_pits[i + 2]) - min(beat_pits[i + 2]) > 4:
                return False
    #no more than 3 half notes
    for i in range(0, len(durs) - 1):
        if durs[i] == 2.0 and durs[i + 1] == 2.0:
            return False
    #no more than 8 quarter notes
    for i in range(0, len(durs) - 9):
        if durs[i] == 1.0 and durs[i + 1] == 1.0 and durs[i + 2] == 1.0 and durs[i + 3] == 1.0 and durs[i + 4] == 1.0 and durs[i + 5] == 1.0 and durs[i+6] == 1.0 and durs[i + 7] == 1.0 and durs[i +8] == 1.0:
            return False
    #no notes lower than -3
    if min(pits) < -3:
        return False
    if max(pits) > 20:
        return False
    for i in range(1, len(cells)):
        if (cells[i - 1].pits[-1] % 7) == 3 and cells[i].chord == [0,2,4] and (cells[i].pits[0] % 7) != 2:
            return False
        if (cells[i - 1].pits[-1] % 7) == 6 and cells[i].chord == [0,2,4] and (cells[i].pits[0] % 7) != 0:
            return False
    if len(cells) > 1:
        if max(pits) - min(pits) < 4:
            return False
    #no doubles of sixteenth notes
    for i in range(1, len(pits)):
        if pits[i] == pits[i - 1] and (durs[i] == 0.25 or durs[i - 1] == 0.25):
            return False
    if melody:
        #no annoying 16ths
        for i in range(0, len(pits) - 3):
            if durs[i] == 0.25 and durs[i + 1] == 0.25 and durs[i + 2] == 0.25 and durs[i + 3] == 0.25:
                if pits[i] == pits[i + 2] and pits[i + 1] == pits[i + 3]:
                    return False
        #no more than 8 eighth notes
        for i in range(0, len(beat_durs) - 3):
            if beat_durs[i] == [0.5,0.5] and beat_durs[i + 1] == [0.5,0.5] and beat_durs[i+2] == [0.5,0.5] and beat_durs[i + 3] == [0.5,0.5]:
                return False
    #no ending on leading tone
    for beat_pit in beat_pits:
        if beat_pit[-1] % 7 == 6:
            return False
    return True
