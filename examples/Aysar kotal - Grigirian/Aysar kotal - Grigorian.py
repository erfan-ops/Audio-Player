from soundtools import Music, SoundBuffer
import numpy as np


m = Music(tempo=132)
m.DEFAULT_VOLUME = 1
m.init()


voice1 = m.square_wave
voice2 = m.fast_triangle_wave
voice3 = m.sawtooth_wave
voice4 = m.organ


def append_arrs(arr: SoundBuffer, /, *bufs: SoundBuffer) -> SoundBuffer:
    for buffer in bufs:
        arr = np.append(arr, buffer)
    
    return arr


def generate_fade_note(note, wave_type, dur=0, vol=0) -> SoundBuffer:
    wave = m.generate_note_buffer(note, wave_type, dur, vol)
    f = int(wave.size/16)
    return m.fade_in_out(wave, f, f)


#-- voice 1 -- #
g3dq = generate_fade_note("g3", voice1, 3)
g3q = generate_fade_note("g3", voice1, 2)
g3e = generate_fade_note("g3", voice1, 1)

a4e = generate_fade_note("a4", voice1, 1)

bb4q = generate_fade_note("a#4", voice1, 2)
bb4e = generate_fade_note("a#4", voice1, 1)
bb4s = generate_fade_note("a#4", voice1, .5)

c4q = generate_fade_note("c4", voice1, 2)
c4de = generate_fade_note("c4", voice1, 1.5)
c4e = generate_fade_note("c4", voice1, 1)
c4s = generate_fade_note("c4", voice1, .5)

d4q = generate_fade_note("d4", voice1, 2)
d4de = generate_fade_note("d4", voice1, 1.5)
d4e = generate_fade_note("d4", voice1, 1)

eb4e = generate_fade_note("d#4", voice1, 1)


voc1p1 = append_arrs(d4q, c4e, eb4e, d4q,
                     c4q, bb4e, d4e, c4q,
                     bb4q, a4e, c4e, bb4q,
                     bb4e, a4e, g3e, g3dq)

voc1p2 = append_arrs(bb4q, bb4e, d4e, c4q,
                     d4de, c4s, bb4e, d4e, c4q,
                     c4de, bb4s, a4e, c4e, bb4e, bb4e,
                     bb4e, a4e, g3e, g3dq)

voc1 = append_arrs(voc1p1, voc1p1, voc1p2, voc1p2)


#-- voice 2 -- #
cs3e = generate_fade_note("c#3", voice2, 1)

d3e = generate_fade_note("d3", voice2, 1)

eb3e = generate_fade_note("d#3", voice2, 1)

fs3e = generate_fade_note("f#3", voice2, 1)

g3q = generate_fade_note("g3", voice2, 2)
g3e = generate_fade_note("g3", voice2, 1)
g3s  = generate_fade_note("g3", voice2, .5)

a4q = generate_fade_note("a4", voice2, 2)
a4e = generate_fade_note("a4", voice2, 1)
a4de = generate_fade_note("a4", voice2, 1.5)
a4s = generate_fade_note("a4", voice2, .5)

bb4q = generate_fade_note("a#4", voice2, 2)
bb4de = generate_fade_note("a#4", voice2, 1.5)
bb4e = generate_fade_note("a#4", voice2, 1)

c4q = generate_fade_note("c4", voice2, 2)
c4de = generate_fade_note("c4", voice2, 1.5)
c4e = generate_fade_note("c4", voice2, 1)


voc2p1 = append_arrs(bb4q, a4e, c4e, bb4q,
                     g3q, g3e, bb4e, a4q,
                     g3q, g3e, g3e, g3q,
                     g3e, eb3e, d3e, d3e, eb3e, d3e)

voc2p2 = append_arrs(g3q, g3e, bb4e, a4q,
                     bb4de, a4s, g3e, bb4e, a4q,
                     a4de, g3s, fs3e, g3e, g3e, g3e,
                     g3e, eb3e, d3e, d3e, cs3e, d3e)

voc2 = append_arrs(voc2p1, voc2p1, voc2p2, voc2p2)


#-- voice 3 --#
a3e = generate_fade_note("a3", voice3, 1)

bb3e = generate_fade_note("a#3", voice3, 1)

c3e = generate_fade_note("c3", voice3, 1)

cs3e = generate_fade_note("c#3", voice3, 1)

d3q = generate_fade_note("d3", voice3, 2)
d3de = generate_fade_note("d3", voice3, 1.5)
d3e = generate_fade_note("d3", voice3, 1)

eb3q = generate_fade_note("d#3", voice3, 2)
eb3e = generate_fade_note("d#3", voice3, 1)
eb3s = generate_fade_note("d#3", voice3, .5)

e3e = generate_fade_note("e3", voice3, 1)

fs3e = generate_fade_note("f#3", voice3, 1)

g3e = generate_fade_note("g3", voice3, 1)

voc3p1 = append_arrs(d3q, eb3e, c3e, d3q,
                     eb3q, d3e, d3e, eb3q,
                     d3q, cs3e, eb3e, d3q,
                     d3e, c3e, bb3e, d3e, cs3e, bb3e)

voc3p2 = append_arrs(d3q, d3e, d3e, eb3q,
                     d3de, eb3s, d3e, e3e, fs3e, g3e,
                     d3de, eb3s, d3e, eb3e, d3e, d3e,
                     d3e, c3e, bb3e, bb3e, a3e, bb3e)

voc3 = append_arrs(voc3p1, voc3p1, voc3p2, voc3p2)


#-- voice 4 --#
fs2de = generate_fade_note("f#2", voice4, 1.5)

g2dq = generate_fade_note("g2", voice4, 3)
g225 = generate_fade_note("g2", voice4, 2.5)
g2q = generate_fade_note("g2", voice4, 2)
g2e = generate_fade_note("g2", voice4, 1)
g2s = generate_fade_note("g2", voice4, .5)

a3e = generate_fade_note("a3", voice4, 1)

bb3e = generate_fade_note("a#3", voice4, 1)
bb3s = generate_fade_note("a#3", voice4, .5)

gggg = append_arrs(g2q, g2e, g2e, g2q)

voc4p1 = append_arrs(gggg,
                     gggg,
                     gggg,
                     g2e, g2e, g2e, bb3s, g225)

voc4p2 = append_arrs(gggg,
                     g2q, g2e, bb3e, a3e, g2e,
                     fs2de, g2s, a3e, g2e, g2e, g2e, g2e, g2q, g2dq)

voc4 = append_arrs(voc4p1, voc4p1, voc4p2, voc4p2)


#-- SONG --#
song = Music.add_multiple_buffers(voc1, voc2, voc3, voc4)

m.play_buffer(song)
# m.export_to_erfan("Aysar kotal - Grigorian.erfan", song, m.sample_rate, m.dtype, 1)

m.done()