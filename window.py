import pyglet, threading
from Tkinter import *

#upload with button click
class Inst:
        def __init__(self, source, tab):
                self.source=source
                self.tab=tab
        def tostring(self):
                return self.source + " " + self.tab

class GarageBandView(pyglet.window.Window):
        """
        A class that defines the UI window for the user
        """
        def __init__(self, player):
                """
                Sets up the window.  Also sets the initial label that will
                be used and schedules the update method to fire every
                60th of a second
                """
                pyglet.window.Window.__init__(self, width=500, height=500)
                self.label = [pyglet.text.Label('Keyboard instructions',
                                               font_name='Times New Roman',
                                               font_size=24,
                                               x=self.width//2,
                                               y=20,
                                               anchor_x='center',
                                               anchor_y='center')]
                self.origlabels = []
                self.label_count = 0
                self.font_size_pix = 16
                self.schedule = pyglet.clock.schedule_interval(
                                func = self.update,
                                interval=1/60.)
                self.current_index = 0
                self.player = player
                self.add_instruments(self.player.instruments)
                self.savetext = ''
                self.saveEnabled = False

        def on_draw(self):
                """
                Draws all the instruments and whatever else to the window
                """
                self.clear()
                for label in self.label:
                        label.draw()

        def on_key_press(self, symbol, modifiers):
                #Check to see if the user hit save.  If yes, handle the user
                #backspacing the filename and hitting enter to complete
                #the save
                if self.saveEnabled:
                    if symbol == pyglet.window.key.ENTER:
                        self.player.save(self.savetext + '.txt')
                        #Switch the labels back to pointing at the ones
                        #before save was enabled
                        self.savetext = ''
                        self.label[0:] = self.origlabels
                        self.saveEnabled = False
                    elif symbol == pyglet.window.key.BACKSPACE:
                        #Remove one character from the save filename
                        self.savetext = self.savetext[:-1]
                        self.label[1].text = self.savetext

        def on_key_release(self, symbol, modifiers):
                string = pyglet.window.key.symbol_string(symbol).strip('_').upper()

                if string.isdigit() and not self.player.is_paused:
                    #Changes the value of the current note
                    self.player.write_note(self.player.instruments[self.current_index], float(string))
                elif string == "DOWN":
                    #Moves the "cursor" down one instrument
                    self.current_index = (self.current_index + 1)%len(self.player.instruments)
                elif string == "UP":
                    #Moves the "cursor" up one instrument
                    self.current_index = self.current_index - 1
                elif string == "SPACE":
                    #Pauses or resumes the music
                    if self.player.is_paused:
                        self.player.resume()
                    else:
                        self.player.pause()
                elif string == "T":
                    #Stops the music
                    self.player.stop()
                elif string == "S":
                    #Changes the labels to show the save UI to the user
                    #and lets the program know that saving is occuring
                    if self.saveEnabled == False:
                        self.origlabels[0:] = self.label
                        self.label[2:] = []
                        self.label[0] = pyglet.text.Label("Type the file name and press enter to save",
                                                      font_name = 'Times New Roman',
                                                      font_size = 16,
                                                      x=20,
                                                      y=self.height//2)
                        self.label[1] = pyglet.text.Label(self.savetext,
                                                      font_name = 'Times New Roman',
                                                      font_size = 12,
                                                      x=50,
                                                      y=self.height//2 - 22)
                        self.saveEnabled = True

        def on_text(self, text):
            #Checks to see if the user has hit save, if yes then adds
            #whatever text is typed into the label that is showing the
            #user's filename
            if self.saveEnabled:
                self.savetext += text
                self.label[1].text = self.savetext

        def update(self, interval):
                """
                Necessary function for the window to redraw itself
                """
                #Checks to see if the labels need to be updated by looking
                #at the player's dirty variable.  If yes, removes all
                #instruments and re-adds them all
                if (self.player.dirty):
                    self.label[1:] = []
                    self.label_count = 0
                    self.add_instruments(self.player.instruments)
                    self.player.dirty = False


        def __inst_spot(self):
                #The value that the next added instrument should have in its
                #y value
                return self.label_count * self.font_size_pix

        def add_instrument(self, instr):
                """
                Add an instrument to the window
                """
                #Creates new label for instrument and appends it to the
                #label list
                self.label_count += 1
                new_label = pyglet.text.Label(str(instr),
                                              font_name = 'Times New Roman',
                                              font_size = 12,
                                              x=10,
                                              y=self.height-self.__inst_spot())
                self.label.append(new_label)

        def add_instruments(self, instruments):
                """
                Adds a list of instruments
                """
                for instrument in instruments:
                        self.add_instrument(instrument)
