from soundtools import Music, SoundBuffer
import numpy as np
from time import perf_counter


m = Music(tempo=138)
m.DEFAULT_VOLUME = 1
m.init()



# -------------- #
# --Empty Town-- #
# -------------- #


def append_arrs(arr: SoundBuffer, /, *bufs: SoundBuffer) -> SoundBuffer:
    for buffer in bufs:
        arr = np.append(arr, buffer)
    
    return arr

def generate_fade_note(note, wave_type, dur=0, vol=0):
    wave = m.generate_note_buffer(note, wave_type, dur, vol)
    f = int(wave.size/16)
    return m.fade_in_out(wave, f, f)


m.DEFAULT_VOLUME = 1

g1_wave = m.fast_triangle_wave


start = perf_counter()


a2q = generate_fade_note("a2", g1_wave, 1)

bb2q = generate_fade_note("a#2", g1_wave, 1)

b2q = generate_fade_note("b2", g1_wave, 1)

c2q = generate_fade_note("c2", g1_wave, 1)

d2s = generate_fade_note("d2", g1_wave, .5)
d2q = generate_fade_note("d2", g1_wave, 1)

e2s = generate_fade_note("e2", g1_wave, 0.5)
e2q = generate_fade_note("e2", g1_wave, 1)

f264 = generate_fade_note("f2", g1_wave, .125)
f2s = generate_fade_note("f2", g1_wave, 0.5)
f2q = generate_fade_note("f2", g1_wave, 1)

fs2q = generate_fade_note("f#2", g1_wave, 1)
fs2h = generate_fade_note("f#2", g1_wave, 2)

g264 = generate_fade_note("g2", g1_wave, .125)
g2s = generate_fade_note("g2", g1_wave, .5)
g2q = generate_fade_note("g2", g1_wave, 1)

gs2s = generate_fade_note("g#2", g1_wave, .5)
gs2q = generate_fade_note("g#2", g1_wave, 1)


a3q = generate_fade_note("a3", g1_wave, 1)

bb3q = generate_fade_note("a#3", g1_wave, 1)

b3s = generate_fade_note("b3", g1_wave, .5)
b3q = generate_fade_note("b3", g1_wave, 1)

c3s = generate_fade_note("c3", g1_wave, .5)
c3q = generate_fade_note("c3", g1_wave, 1)
c3h = generate_fade_note("c3", g1_wave, 2)

d3s = generate_fade_note("d3", g1_wave, .5)

ds3q = generate_fade_note("d#3", g1_wave, 1)
ds3h = generate_fade_note("d#3", g1_wave, 2)

e3s = generate_fade_note("e3", g1_wave, .5)
e3q = generate_fade_note("e3", g1_wave, 1)

f3s = generate_fade_note("f3", g1_wave, .5)
f3q = generate_fade_note("f3", g1_wave, 1)
f3h = generate_fade_note("f3", g1_wave, 2)

g3s = generate_fade_note("g3", g1_wave, 0.5)
g3q = generate_fade_note("g3", g1_wave, 1)
g3h = generate_fade_note("g3", g1_wave, 2)
g3dh = generate_fade_note("g3", g1_wave, 3)

gs3s = generate_fade_note("g#3", g1_wave, .5)


a4s = generate_fade_note("a4", g1_wave, 0.5)
a4q = generate_fade_note("a4", g1_wave, 1)
a4h = generate_fade_note("a4", g1_wave, 2)

bb4s = generate_fade_note("a#4", g1_wave, .5)
bb4q = generate_fade_note("a#4", g1_wave, 1)
bb4h = generate_fade_note("a#4", g1_wave, 2)

b4s = generate_fade_note("b4", g1_wave, 0.5)
b4q = generate_fade_note("b4", g1_wave, 1)
b4dh = generate_fade_note("b4", g1_wave, 3)

c4s = generate_fade_note("c4", g1_wave, 0.5)
c4q = generate_fade_note("c4", g1_wave, 1)
c4dq = generate_fade_note("c4", g1_wave, 1.5)
c4h = generate_fade_note("c4", g1_wave, 2)
c4dh = generate_fade_note("c4", g1_wave, 3)

d4s = generate_fade_note("d4", g1_wave, .5)
d4q = generate_fade_note("d4", g1_wave, 1)
d4h = generate_fade_note("d4", g1_wave, 2)

ds4q = generate_fade_note("d#4", g1_wave, 1)

e4s = generate_fade_note("e4", g1_wave, 0.5)
e4q = generate_fade_note("e4", g1_wave, 1)
e4dq = generate_fade_note("e4", g1_wave, 1.5)
e4h = generate_fade_note("e4", g1_wave, 2)
e4dh = generate_fade_note("e4", g1_wave, 3)

f4s = generate_fade_note("f4", g1_wave, 0.5)
f4q = generate_fade_note("f4", g1_wave, 1)
f4h = generate_fade_note("f4", g1_wave, 2)

g4s = generate_fade_note("g4", g1_wave, 0.5)
g4q = generate_fade_note("g4", g1_wave, 1)
g4h = generate_fade_note("g4", g1_wave, 2)


a5s = generate_fade_note("a5", g1_wave, .5)
a5q = generate_fade_note("a5", g1_wave, 1)

b5s = generate_fade_note("b5", g1_wave, .5)
b5q = generate_fade_note("b5", g1_wave, 1)
b5h = generate_fade_note("b5", g1_wave, 2)
b5dh = generate_fade_note("b5", g1_wave, 3)

c5s = generate_fade_note("c5", g1_wave, .5)
c5q = generate_fade_note("c5", g1_wave, 1)
c5h = generate_fade_note("c5", g1_wave, 2)

d5dh = generate_fade_note("d5", g1_wave, 3)


restq = generate_fade_note(0, m.sine_wave, 1)


g1_p1 = append_arrs(a4h, c4s, e4s,
                    c5h, b5q,
                    g4h, d4q,
                    e4dh,
                    e4h, f4s, g4s,
                    f4h, e4q,
                    d4h, c4q,
                    e4dh)
g1_p1 = np.append(g1_p1, g1_p1)
g1_comp = append_arrs(c3h, a4s, b4s,
                      e4h, e4q,
                      d4h, b4q,
                      a4h, g3q,
                      a4h, a4s, b4s,
                      c4h, b4q,
                      g3h, e3q,
                      b4dh,
                      f3h, f3s, g3s,
                      a5q, g4q, f4q,
                      e4q, d4s, c4s, b4s, a4s,
                      g3dh,
                      a4h, bb4s, c4s,
                      bb4h, a4q,
                      a4h, gs3s, a4s,
                      b4dh)
motif = append_arrs(restq, b5s, c5s, b5s, a5s)
g1_p3 = append_arrs(motif,
                    e4q, c4q, e4q,
                    motif,
                    d5dh,
                    motif,
                    b5h, c5q,
                    g4q, g4s, f4s, e4s, f4s,
                    e4dh,
                    restq, e4s, f4s, e4s, d4s,
                    bb4q, f3q, f4q,
                    e4dq, d4s, c4s, d4s,
                    e4h, c4q,
                    ds4q, b4q, a4q,
                    ds3h, ds4q)
g1_p3 = append_arrs(g1_p3, e4dh, e2q, fs2q, gs2q,
                    g1_p3, e4dh, e4s, d4s, c4s, d4s, c4s, gs3s)


g2_p2 = g1_p1

g2_p3 = append_arrs(restq, d4s, e4s, d4s, c4s,
                    b4q, a4q, b4q,
                    restq, d4s, e4s, d4s, c4s,
                    b5dh,
                    restq, g4s, a5s, g4s, f4s,
                    g4h, a5q,
                    e4q, e4s, d4s, c4s, d4s,
                    c4dh,
                    restq, c4s, d4s, c4s, bb4s,
                    f3q, bb3q, d4q,
                    c4dq, b4s, a4s, b4s,
                    c4h, a4q,
                    b4q, ds3q, c3q,
                    fs2h ,b4q,
                    a4h, gs3s, a4s)
g2_p3 = append_arrs(g2_p3, b4dh,
                    g2_p3, c4s, b4s, a4s, b4s, a4s, e3s)


aee = np.append(a3q, [e3q, e3q])
gee = np.append(g2q, [e3q, e3q])
fcc = np.append(f2q, [c3q, c3q])
ebb = np.append(e2q, [b3q, b3q])
daa = np.append(d2q, [a3q, a3q])
cgg = np.append(c2q, [g2q, g2q])
bbff = np.append(bb2q, [f2q, f2q])
eaa = np.append(e2q, [a3q, a3q])
egg = np.append(e2q, [gs2q, gs2q])
ebcdb = np.append(e2q, [b3s, c3s, d3s, b3s])
fee = np.append(f2q, [e3q, e3q])
fce = np.append(f2q, [c3q, e3q])
ornam = append_arrs(g2s, f264, g264, f264, g264, e2s, f2s, e2s, d2s)
bdf = np.append(bb2q, [d2q, f2q])
ace = np.append(a2q, [c2q, e2q])
bff = np.append(b2q, [fs2q, fs2q])
edcdcgs = np.append(e3s, [d3s, c3s, d3s, c3s, gs2s])

g3_p1n2 = np.append(aee, [aee,
                    gee, gee,
                    fcc, fcc,
                    ebb, ebb,
                    daa, daa,
                    cgg, cgg,
                    bbff, bbff,
                    eaa, egg,
                    
                    aee, aee,
                    gee, gee,
                    fcc, fcc,
                    ebb, ebcdb,
                    daa, daa,
                    cgg, cgg,
                    bbff, bbff,
                    eaa, egg])

g3_p3 = append_arrs(aee, aee,
                    gee, gee,
                    fee, fee,
                    cgg, ornam,
                    bdf, bdf,
                    ace, ace,
                    bff, bff,
                    ebb, edcdcgs)
g3_p3 = np.append(g3_p3, g3_p3)

g3 = np.append(g3_p1n2, g3_p3)


p2 = Music.add_buffers(g2_p2, g1_comp)
p3 = Music.add_buffers(g2_p3, g1_p3)

song = append_arrs(g1_p1,
                   p2,
                   p3)

song = Music.add_buffers(song, g3) / 3


end = perf_counter()

print(f"{round(end-start, 2)} s")

# m.export_to_erfan("Empty Town - Toby Fox", song, m.default_sample_rate, m.dtype, 1)
m.play_buffer(song)

m.done()