#!/usr/bin/env python

"""
SLEEP OR SOMETING
"""
import pyglet, sys, threading, time
from threading import Semaphore
from pyglet import media

string_sources = []
string_tabs = []
players = []
players_count = 0
barrier = None
play_lock = threading.Lock()


# MAKE NOTE THAT YOU FOUND THIS SOLUTION
# http://stackoverflow.com/questions/26622745/implementing-barrier-in-python2-7
class Barrier:
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
    global player

    #TODO handling incorrect usage
    read_input(args[1])
    create_players()

    play()


def read_input(filepath):
    with open(filepath) as f:
        for line in f:
            temp = line.split(" ")
            add_source(temp[0])
            add_tab(temp[1])

def add_source(source_path):
    global string_sources
    string_sources.append(media.load(source_path, streaming=False))

def add_tab(tab_input):
    global string_tabs
    tab = tab_input.replace('|', '')
    string_tabs.append(tab)

def create_players():
    global players, players_count
    for i in xrange(len(string_tabs)):
        player = media.Player()
        player.eos_action = media.Player.EOS_PAUSE
        players.append(player)
        players_count += 1
    # queue sources
    for i, player in enumerate(players):
        player.queue(string_sources[i])

def queue_next_sounds(next_note_index):
    global players, players_count
    for i, tab in enumerate(string_tabs):
        #print "----------"
        if next_note_index >= len(tab):
            players[i] = None
            players_count -= 1
        elif tab[next_note_index].isdigit():
        #    print tab[next_note_index]
            players[i].pitch = shift_pitch(float(tab[next_note_index]))
            players[i].volume = 1.0
        else:
        #    print tab[next_note_index]
            players[i].volume = 0.0
    #print "*************************"
    #print "*************************"
    #print "*************************"

def shift_pitch(note):
    """
    Note: this only works on pitche shifts 0-9
    """
    return 2**(note/12)

def play():
    global players, barrier
    note_index = 0
    while players_count > 0:
        barrier = Barrier(players_count)
        queue_next_sounds(note_index)
        asynchonrously_play_next_note()
        note_index += 1


def asynchonrously_play_next_note():
    """
        Initialize and run each thread to perform fun on a particular string
    """
    global players
    threads = list()
    for i, player in enumerate(players):
        if player is not None:
            threads.append(
                threading.Thread(target = play_sound, args = [i]))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    for player in players:
        if player is not None:
            player.seek(0.0)

def play_sound(index):
    global players, barrier
    barrier.wait()
    players[index].play()
    time.sleep(0.16)

if __name__ == '__main__':
    main(sys.argv)
