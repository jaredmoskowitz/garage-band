#!/usr/bin/env python
"""
rockband.py

Jared Moskowitz
10/18/16
COMP 50: Concurrent Programming

This program plays the given instrument tablature concurrently

"""
import pyglet, sys, threading, time, Queue, random
from threading import Semaphore
from pyglet import media
from pyglet.window import key
from pyglet.window import mouse


instruments = []
active_instrument_count = 0 # # of instruments planning to play their next note
barrier = None
write_queue = Queue.Queue()
music_length = 0

class Instrument:
    """
    Owns a source, tabulatur (string), and a player
    """
    def __init__(self, source_path, tab):
        self.source_path = source_path
        self.source = media.load(source_path, streaming=False)
        self.tab = tab
        self.player = media.Player()
        self.player.eos_action = media.Player.EOS_PAUSE
        self.player.queue(self.source)

    def __str__(self):
        return self.source_path + " " + self.tab

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
    global instruments

    # check for correct input
    if len(args) > 2:
        print "Input Error: incorrect number of arguments"
        usage_string = "USGAE: ./rockband.py [music text file] "
        print usage_string
        exit(0)


    sources, tabs = read_input(args[1])
    instruments = create_instruments(sources, tabs)
    play()

def read_input(filepath):
    """
    parse the file at the given path to obtain sources and tabs
    """
    global music_length

    music_length = 0
    sources = list()
    tabs = list()
    with open(filepath) as f:
        for line in f:
            temp = line.strip().split(" ")
            print temp
            sources.append(temp[0])
            string = temp[1].replace('|', '')
            music_length = len(string) if len(string) > music_length else music_length
            tabs.append(temp[1].replace('|', ''))

    # make all intruments same length
    for tab in tabs:
        if len(tab) < music_length:
            tab = tab + ''.join(['x']*(music_length - len(tab)))
    return sources, tabs

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
    for instr in instruments:
        if instr.tab[note_i].isdigit():
            instr.player.pitch = shift_pitch(float(instr.tab[note_i]))
            instr.player.volume = 1.0
        else:
            # instrument isn't supposed to play the next note, so silence it
            instr.player.volume = 0.0

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
    global active_instrument_count, instruments, barrier
    note_index = 0
    active_instrument_count = len(instruments)

    while note_index < music_length : # play until no one needs no more music
        barrier = Barrier(active_instrument_count)
        queue_next_sounds(note_index)
        asynchonrously_play_next_note()
        write_music(note_index)
        print note_index

        note_index += 1 # iterate through the notes
        output()

    play() # loop

def asynchonrously_play_next_note():
    """
        Call the instruments so they all play their next note at the same time
    """
    global instruments, write_queue
    threads = list()
    for instrument in instruments:
        threads.append(
            threading.Thread(target = play_sound, args = [instrument]))
        # else: these would be the instruments that have reached the end of
        # their music tab
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for instrument in instruments:
        instrument.player.seek(0.0)

def write_music(note_index):
    global instruments
    write_note(instruments[2], random.randint(1, 9))

    while(not write_queue.empty()):
        (instrument, pitch) = write_queue.get()
        instrument.player.pitch = shift_pitch(pitch)
        tab = list(instrument.tab)
        tab[note_index] = str(int(pitch))
        instrument.tab = ''.join(tab)

def play_sound(instrument):
    """
    play sound for instrument in sync with all other threads running this
    function
    """
    global instruments, barrier
    barrier.wait()
    instrument.player.play()
    time.sleep(0.15)

def pause():
    """
    Pause the music until resume is pushed
    """
    return None

def resume():
    """
    Play the music if already paused.
    If already resumed then no action will be taken
    """
    return None

def write_note(instrument, pitch):
    """
    Changes given instrument to given pitch for current index
    in tab
    """
    global write_queue
    write_queue.put((instrument, pitch))

def stop():
    """
    Stops the music.
    """
    return None

def save(filename):
    """
    saves current tab to text file in given filename
    """
    return None

def get_sheet_music():
    sheet = ""
    for instrument in instruments:
        sheet += str(instrument) + "\n"
    return sheet

def output():
    print get_sheet_music()

if __name__ == '__main__':
    main(sys.argv)
