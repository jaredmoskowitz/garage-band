#!/usr/bin/env python
"""
garageband.py

Jared Moskowitz and Nick Carlino
12/07/16
COMP 50: Concurrent Programming

This program reads, plays, controls, writes, and outputs
the given instrument tablature concurrently.

"""
import pyglet, sys, threading, time, Queue, random, window
from window import GarageBandView
from threading import Semaphore
from pyglet import media
from pyglet.window import key
from pyglet.window import mouse

thread = None



class Instrument:
    """
    Owns a source, tabulatur (string), and a player
    """
    def __init__(self, source_path, tab):
        self.source_path = source_path
        self.source = media.load(source_path, streaming=False)
        self.tab = tab
        self.player = media.Player()
        self.player.eos_action = media.Player.EOS_LOOP
        self.player.queue(self.source)

    def load_source(self):
        self.player.queue(self.source)

    def __str__(self):
        return self.source_path + " " + self.tab

class Barrier:
    """
    Class implementation of a barrier anwser (accidently) obtained from
    stackoverflow.com/questions/26622745/implementing-barrier-in-python2-7
    """
    def __init__(self, n):
        self.count = 0
        self.cap = n
        self.mutex = Semaphore(1)
        self.barrier = Semaphore(0)
        self.note_index = 0
    def wait(self):
        self.mutex.acquire()
        self.count = self.count + 1
        self.mutex.release()
        if self.count == self.cap:
            self.barrier.release()
        self.barrier.acquire()
        self.barrier.release()

class Player:
    """
    Plays a group of instruments together. Furthermore, allows ability to
    control music, write music, and save the new music to a file.
    """
    def __init__(self, instruments):
        self.instruments = instruments
        self.barrier = None
        self.write_queue = Queue.Queue()
        self.action_queue = Queue.Queue()
        self.music_length = \
                        0 if len(instruments) == 0 else len(instruments[0].tab)
        self.paused = Semaphore(1)
        self.is_paused = False
        self.dirty = False
        self.note_index = 0
        self.compound_note_index = 0
        self.is_quitting = False


    def queue_next_sounds(self, note_i):
        """
        Change the pitch and volume of the instruments to set up playing for
        the next note
        """
        for instr in self.instruments:
            if instr.tab[note_i].isdigit():
                instr.player.pitch = self.shift_pitch(float(instr.tab[note_i]))
                instr.player.volume = 1.0
            else:
                #instrument isn't supposed to play the next note, so silence it
                instr.player.volume = 0.0

    def shift_pitch(self, note):
        """
        Change the pitch from the nominal pitch
        NOTE: this only works on pitche shifts 0-9
        """
        return 2**(note/12)

    def play(self, start_index = 0):
        """
        use all the instruments concurrently to play the music in harmony
        """
        global instruments, barrier

        self.note_index = start_index

        instruments_count = len(self.instruments)

        while self.note_index < music_length :
            self.barrier = Barrier(instruments_count)
            self.queue_next_sounds(self.note_index)
            self.asynchonrously_play_next_note()

           # perform actions user inputted while playing music at current index
            self.action_queue.put(self.write_music_action)
            self.perform_input_actions()

            if self.is_quitting:
                return

            self.paused.acquire()
            self.paused.release() #turnstile

            self.note_index += 1 # iterate through the notes
            self.compound_note_index += 1 # used by window for scrolling
                                          # larger UI on larger songs

        self.play()

    def asynchonrously_play_next_note(self):
        """
        Calls the instruments so they all play their next note at the same time
        """
        threads = list()
        for instrument in self.instruments:
            threads.append(
                threading.Thread(target = self.play_sound,
                                 args = [instrument]))
            # else: these would be the instruments that have reached the end of
            # their music tab
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        for instrument in self.instruments:
            try:
                instrument.player.seek(0.0)
            except AttributeError: # handles pyglet error where finishes source
                instrument.load_source()
                instrument.player.volume = 1.0

    def perform_input_actions(self):
        """
        executes input actions given by
        """
        while not self.action_queue.empty():
            callback = self.action_queue.get()
            callback()

    def play_sound(self, instrument):
        """
        plays sound for instrument in sync with all other threads running this
        function
        """
        self.barrier.wait()
        instrument.player.play()
        time.sleep(0.15)

    def pause(self):
        """
        Pauses the music until resume is pushed
        """
        self.is_paused = True
        self.paused.acquire()

    def resume(self):
        """
        Plays the music if already paused.
        If already resumed then no action will be taken
        """
        self.is_paused = False
        self.paused.release()

    def write_note(self, instrument, pitch):
        """
        Queues instrument to change pitch at current note index
        """
        self.write_queue.put((instrument, pitch))

    def write_music_action(self):
        """
        Changes the given instruments to given pitchs for current index
        in tab
        """
        while(not self.write_queue.empty()):
            (instrument, pitch) = self.write_queue.get()
            tab = list(instrument.tab)
            tab[self.note_index] = str(int(pitch))
            instrument.tab = ''.join(tab)
            self.dirty = True

    def move_right(self):
        self.action_queue.put(self.right_action)

    def right_action(self):
        """
        moves current note index to the right
        """
        if self.note_index >= self.music_length - 1:
            self.note_index = 0
            self.compound_note_index = 0
        else:
            self.note_index = self.note_index + 1
            self.compound_note_index = self.compound_note_index + 1

    def move_left(self):
        self.action_queue.put(self.left_action)

    def left_action(self):
        """
        moves current note index to the left
        """
        if self.note_index > 0:
            self.note_index = self.note_index - 1
            self.compound_note_index = self.compound_note_index - 1
        else:
            self.note_index = self.music_length - 1
            self.compound_note_index = self.music_length - 1

    def save(self, filename):
        """
        saves current tab to text file in given filename
        """
        f = open(filename,'w')
        f.write(self.get_sheet_music()) # python will convert \n to os.linesep
        f.close() # you can omit in most cases as the destructor will call it

    def get_sheet_music(self):
        """
        returns the current music in the form of a string
        """
        sheet = ""
        for instrument in self.instruments:
            sheet += str(instrument) + "\n"
        return sheet

    def quit(self):
        """
        Stops the music from playign and exits the program
        """
        self.action_queue.put(self.quit_action)

    def quit_action(self):
        self.is_quitting = True

def main(args):
    global instruments, thread

    # check for correct input
    if len(args) > 2:
        print "Input Error: incorrect number of arguments"
        usage_string = "USGAE: ./rockband.py [music text file] "
        print usage_string
        exit(0)

    # create instrument instances from input file
    sources, tabs = read_input(args[1])
    instruments = create_instruments(sources, tabs)

    player = Player(instruments)

    window = GarageBandView(player)

    def play_main(p):
        p.play()

    # run Player and window on seperate threads
    thread = threading.Thread(target = play_main, args = [player])
    thread.start()
    pyglet.app.run()

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
            sources.append(temp[0])
            string = temp[1].replace('|', '')
            music_length = \
                    len(string) if len(string) > music_length else music_length
            tabs.append(string)

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


if __name__ == '__main__':
    main(sys.argv)
