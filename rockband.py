#!/usr/bin/env python
"""
rockband.py

Jared Moskowitz
10/18/16
COMP 50: Concurrent Programming

This program plays the given instrument tablature concurrently

"""
import pyglet, sys, threading, time
from threading import Semaphore
from pyglet import media
from pyglet.window import key
from pyglet.window import mouse


instruments = []
active_instrument_count = 0 # # of instruments planning to play their next note
barrier = None

window = pyglet.window.Window()

label = pyglet.text.Label('Hello, world',
                          font_name='Times New Roman',
                          font_size=36,
                          x=window.width//2, y=window.height//2,
                          anchor_x='center', anchor_y='center')

class Instrument:
    """
    Owns a source, tabulatur (string), and a player
    """
    def __init__(self, source, tab):
        self.source = source
        self.tab = tab
        self.player = media.Player()
        self.player.eos_action = media.Player.EOS_PAUSE
        self.player.queue(self.source)

class Barrier:
    """
   Class implementation of a barrier anwser (accidently) obtained from
   http://stackoverflow.com/questions/26622745/implementing-barrier-in-python2-7
   """
    def __init__(self, n):
        self.count = 0
        self.cap = n
        self.mutex = Semaphore(1)
        self.barrier = Semaphore(0)
    def wait(self):
        self.mutex.acquire()
        self.count = self.count + 1
        self.mutex.release()
        if self.count == self.cap:
            self.barrier.release()
        self.barrier.acquire()
        self.barrier.release()

def main(args):
    global active_instrument_count, instruments

    # check for correct input
    if len(args) > 2:
        print "Input Error: incorrect number of arguments"
        usage_string = "USGAE: ./rockband.py [music text file] "
        print usage_string
        exit(0)


    sources, tabs = read_input(args[1])
    instruments = create_instruments(sources, tabs)
    active_instrument_count = len(instruments)

    play()

def read_input(filepath):
    """
    parse the file at the given path to obtain sources and tabs
    """
    sources = list()
    tabs = list()
    with open(filepath) as f:
        for line in f:
            temp = line.split(" ")
            sources.append(add_source(temp[0]))
            tabs.append(add_tab(temp[1]))
    return sources, tabs

def add_source(source_path):
    """
    create a source given a string path to the audio file
    """
    return media.load(source_path, streaming=False)

def add_tab(tab_input):
    """
    parse the tab_input to create a tab the program can understand
    """
    global string_tabs
    return tab_input.replace('|', '')

def create_instruments(sources, tabs):
    """
    create and return a list of instruments associated with the given
    sources and tabs
    """
    parts = list()
    for i, source in enumerate(sources):
        parts.append(Instrument(source, tabs[i]))
    return parts

def queue_next_sounds(note_i):
    """
    Change the pitch and volume of the instruments to set up playing for
    the next note
    """
    global instruments, active_instrument_count
    for i, instr in enumerate(instruments):
        if note_i >= len(instr.tab): # the instrument has reached the end
            instruments[i].player = None
            active_instrument_count -= 1 # don't factor into the next barrier
        elif instr.tab[note_i].isdigit():
            instruments[i].player.pitch = shift_pitch(float(instr.tab[note_i]))
            instruments[i].player.volume = 1.0
        else:
            # instrument isn't supposed to play the next note, so silence it
            instruments[i].player.volume = 0.0

def shift_pitch(note):
    """
    Change the pitch from the nominal pitch
    NOTE: this only works on pitche shifts 0-9
    """
    return 2**(note/12)

def play():
    """
    use all the instruments concurrently to play the music in harmony
    """
    global instruments, barrier
    note_index = 0
    while active_instrument_count > 0: # play until no one needs no more music
        barrier = Barrier(active_instrument_count)
        queue_next_sounds(note_index)
        asynchonrously_play_next_note()
        note_index += 1 # iterate through the notes
    play()


def asynchonrously_play_next_note():
    """
        Call the instruments so they all play their next note at the same time
    """
    global instruments
    threads = list()
    for i, instrument in enumerate(instruments):
        if instrument.player is not None:
            threads.append(
                threading.Thread(target = play_sound, args = [i]))
        # else: these would be the instruments that have reached the end of
        # their music tab
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for instrument in instruments:
        if instrument is not None:
            instrument.player.seek(0.0)

def play_sound(index):
    """
    play sound for instrument in sync with all other threads running this
    function
    """
    global instruments, barrier
    barrier.wait()
    instruments[index].player.play()
    time.sleep(0.15)

if __name__ == '__main__':
    main(sys.argv)
