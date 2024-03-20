import numpy as np
from math import ceil, floor
import sys
import os
sys.path.append(os.path.split(os.path.split(__file__)[0])[0])
from music import Music



m = Music(tempo=108)
m.DEFAULT_VOLUME = 1
m.init()


# halves the wave duration
def half(wave: np.ndarray):
    return wave[0:len(wave)//2]

# doubles the wave duration
def double(wave: np.ndarray[np.floating]) -> np.ndarray:
    return np.append(wave, wave)

# makes the note shorter and adds "rest" to rest of it to make the sound "staccato" as musicians say
def staccato(wave: np.ndarray, dur: float, play_time: float=0.75):
    playing = len(wave)*play_time
    resting = (1-play_time)*dur
    return np.append(wave[0:floor(playing)], m.generate_note_buffer(0, m.sine_wave, resting))

# these are enharmonic notes so their frequencys are the same in any equal temperament
m._NOTES["eb5"] = m._NOTES["d#5"]

# you can change the wave types
chord_wave = m.sawtooth_wave
note_wave = m.square_wave


fmaj = m.generate_chord_buffer(("c3", "f3", "a4"), chord_wave, 2) * 3/4
f4 = m.generate_note_buffer("f4", note_wave, 2)
# dividing the note decreases the amplitude aka volume
# we multiply the chord amplitude by 3/4 and the note amplitude by 4, so when we add them the amplitude will not be so loud
ch1 = fmaj + f4/4

c5 = m.generate_note_buffer("c5", note_wave, 2)
ch2 = fmaj + c5/4


gmaj = m.generate_chord_buffer(("d3", "g3", "b4"), chord_wave, 1) * 3/4
e5 = m.generate_note_buffer("e5", note_wave, 1)
ch3 = gmaj + e5/4

g5 = m.generate_note_buffer("g5", note_wave, 1)
ch4 = gmaj + g5/4

d5 = m.generate_note_buffer("d5", note_wave, 1)
ch5 = half(gmaj + d5/4)

c5 = m.generate_note_buffer("c5", note_wave, 1)

# "c5[0:len(c5)//4]" this will make the note duration shorter
# and you'll see that i added 1 to the length and that because when you divide it by 4 it rounds it down :(
ch6 = gmaj + np.append(c5[0:len(c5)//4+1], m.generate_note_buffer(0, m.sine_wave, 0.75)) / 4

# this one has 5 notes to we divide by 5
edom7 = m.generate_chord_buffer(("e3", "g#3", "b4", "d4"), chord_wave, 1) * 4/5
ch7 = half(edom7)
ch8 = edom7 + e5/5
ch9 = half(edom7 + c5/5)

f5 = m.generate_note_buffer("f5", note_wave, 1)

# this is a "grace note" or sometimes refferd as n "appoggiatura"
orn_e5_f5 = np.append(e5[0:round(len(e5)/8)], f5[0:round(len(f5)*3/8)])
ch10 = half(edom7) + orn_e5_f5/5


amin = m.generate_chord_buffer(("e3", "a4", "c4"), chord_wave, 1) * 3/4
a5 = m.generate_note_buffer("a5", note_wave, 1)

# making the note just a little staccato so it doesn't connect to the note after it which is the same note
st_a5 = staccato(a5, 1, 0.95)

ch11 = half(amin + st_a5/4)
ch12 = half(amin + a5/4)

a6 = m.generate_note_buffer("a6", note_wave, 1)
ch13 = half(amin + a6/4)
ch14 = half(amin + e5/4)


emin7 = m.generate_chord_buffer(("e3", "g3", "b4", "d4"), chord_wave, 1) * 4/5
ch15 = emin7[0:len(emin7)//4] + e5[0:len(e5)//4]/5

eb5 = m.generate_note_buffer("eb5", note_wave, 1)
ch16 = half(emin7) + eb5[0:len(eb5)//2]/5
ch17 = emin7[0:len(emin7)//4] + d5[0:len(d5)//4]/5
ch18 = half(emin7 + c5/5)

b5 = m.generate_note_buffer("b5", note_wave, 1)
ch19 = half(emin7 + b5/5)

# thats literally a series of notes
series = np.append(f4[0:len(f4)//4+2], [half(a5), half(c5), half(a5)])
ch20 = fmaj + series/4

series = np.append(d5[0:ceil(len(d5)/8)+1], [c5[0:floor(len(c5)/8)], b5[0:floor(len(b5)/8)], b5[0:floor(len(b5)/8)]])
# series = np.append(c5[0:ceil(len(c5)/8)+1], [d5[0:floor(len(d5)/8)], b5[0:floor(len(b5)/8)], b5[0:floor(len(b5)/8)]])
series = np.append(series, half(b5))
ch21 = edom7 + series/5

gs4 = m.generate_note_buffer("g#4", note_wave, 1)
series = np.append(gs4[0:len(gs4)//2+3], [half(b5), half(e5), half(eb5), half(d5), half(b5)])
ch22 = np.append(edom7, [edom7, edom7]) + series/5


series = np.append(staccato(c5[0:len(c5)*3//4+4], 0.75, 0.25), staccato(c5[0:len(c5)*3//4+1], 0.75, 0.25))
series = np.append(series, half(d5))
ch23 = double(amin) + series/4

series = np.append(staccato(half(c5), 0.5, 0.5), [d5[0:len(d5)//4+1], c5[0:len(c5)//4+1]])
ch24 = amin + series/4

series = np.append(half(f5), [e5[0:len(e5)//4+1], eb5[0:len(eb5)//4+1]])
ch25 = amin + series/4

ch26 = m.generate_chord_buffer(("e3", "a4", "c4"), chord_wave, 2)*3/4 + m.generate_note_buffer("e5", note_wave, 2)/4

# you can append the all at once because the length if the chords are different :(
song = np.append(ch1, ch2)
song = np.append(song, [ch3, ch4])
song = np.append(song, ch5)
song = np.append(song, ch6)
song = np.append(song, [ch5, ch7])
song = np.append(song, ch8)
song = np.append(song, ch9)
song = np.append(song, ch10)
song = np.append(song, ch8)
song = np.append(song, ch9)
song = np.append(song, [ch11, ch12, ch13, ch14])
song = np.append(song, ch15)
song = np.append(song, ch16)
song = np.append(song, ch17)
song = np.append(song, [ch18, ch19])
song = np.append(song, [fmaj, ch20])
song = np.append(song, ch21)
song = np.append(song, ch22)
song = np.append(song, ch23)
song = np.append(song, [ch24, ch25])
song = np.append(song, ch26)


m.play_buffer(song)


#-- exports the song to a .erfan file which is completely useless but you can use the app to play them (erfan is my name btw) --#
#-- you can also export to wav, and you can export to [mp3, m4a, aac, wma, ogg, aiff, aifc, aif, flac] and maybe some other formats i don't remember--#
# m.export_to_erfan("last breath - test", song, 48000, "float32", 1)

m.done()