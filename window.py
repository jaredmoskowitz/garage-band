import pyglet

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
        pyglet.window.Window.__init__(self, width=720, height=500)
        self.colors = {
                        'white': (255, 255, 255, 255),
                        'black': (0, 0, 0, 255)
                      }
        self.font_name = 'Times New Romans'
        self.background = 'white'
        self.font_color = 'black'
        #Sets the window color
        pyglet.gl.glClearColor(*self.colors[self.background])
        self.instruction_anchor = 'center'
        #Keyboard instructions for the user
        self.instructions = """
                            -0-9 to write a note
                            -up and down to change instrument
                            -left and right to change note
                            -space to pause/resume
                            -s to save the song
                            -escape to quit
                            """
        #The origin label.  Shows instructions
        self.label = [pyglet.text.Label(self.instructions,
                                        font_name = self.font_name,
                                        font_size = 12,
                                        width = 450,
                                        x = 100,
                                        y = 70,
                                        anchor_x = self.instruction_anchor,
                                        anchor_y = self.instruction_anchor,
                                        multiline = True,
                                        color = self.colors[self.font_color])]
        #Will hold the tabs if labels need to be switched
        self.origlabels = []
        #Extra tabs for when the tab is too long for the window
        self.extras = []
        #The max length of each instruments tab
        self.x_lengths = []
        #Count of instruments
        self.label_count = 0
        #Font size of instruments in pixels
        self.font_size_pix = 22
        #Calls the function update every 15/100 seconds
        self.schedule = pyglet.clock.schedule_interval(func=self.update,
                                                       interval=15/100.)
        #Which instrument the writer is at
        self.current_index = 0
        #The player to interact with
        self.player = player
        #The maximum length of a label
        self.max_tab_length = 63
        self.add_instruments(self.player.instruments)
        #Will hold the name of the file to save to
        self.savetext = ''
        self.saveEnabled = False
        self.firstIter = True

    def on_close(self):
        self.player.quit()

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
                text = self.savetext+'.txt'
                self.player.save(text)
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

        if string.isdigit():
            #Changes the value of the current note
            self.player.write_note(self.player.instruments[self.current_index], float(string))
        elif string == "DOWN":
            #Moves the "cursor" down one instrument
            self.current_index = (self.current_index + 1)%len(self.player.instruments)
        elif string == "UP":
            #Moves the "cursor" up one instrument
            self.current_index = self.current_index - 1
        elif string == "RIGHT":
            #Moves index right one and checks if the tab needs to be
            #redrawn
            self.player.move_right()
            self.__check_pos('right')
        elif string == "LEFT":
            #Same as above but left
            self.player.move_left()
            self.__check_pos('left')
        elif string == "SPACE":
            #Pauses or resumes the music
            if self.player.is_paused:
                self.player.resume()
            else:
                self.player.pause()
        elif string == "S":
            #Changes the labels to show the save UI to the user
            #and lets the program know that saving is occuring
            if self.saveEnabled == False:
                self.origlabels[0:] = self.label
                self.label[2:] = []
                prompt = "Type the file name and press enter to save"
                self.label[0] = pyglet.text.Label(prompt,
                                                  font_name = self.font_name,
                                                  font_size = 16,
                                                  x = 20,
                                                  y = self.height//2,
                                                  color = self.colors[self.font_color])
                self.label[1] = pyglet.text.Label(self.savetext,
                                                  font_name = self.font_name,
                                                  font_size = 12,
                                                  x=50,
                                                  y=self.height//2 - 22,
                                                  color=self.colors[self.font_color])
                self.saveEnabled = True
        elif string == "ESCAPE":
            self.player.quit()
            self.close()

    def on_text(self, text):
        #Checks to see if the user has hit save, if yes then adds
        #whatever text is typed into the label that is showing the
        #user's filename
        if self.saveEnabled:
            self.savetext += text
            self.label[1].text = self.savetext

    def update(self, interval):
        """
        Function that fires every scheduled interval
        """
        #Makes sure that the program doesn't change the tab on the
        #first iteration
        if self.player.note_index != 0:
            self.firstIter = False

        #Checks to see if the labels need to be updated by looking
        #at the player's dirty variable.  If yes, removes all
        #instruments and re-adds them all
        if (self.player.should_update_label):
            self.label[1:] = []
            self.label_count = 0
            self.add_instruments(self.player.instruments)
            self.player.dirty = False

        #Makes sure it is not the first iteration, then checks to
        #see if the tabs need to be redrawn
        if not self.firstIter:
            if not self.saveEnabled:
                self.__check_pos('right')

    def __check_pos(self, direct):
        """
        Checks to see if the tabs need to be redrawn and calls redraw
        functions if yes
        """
        for i in range(0, len(self.player.instruments)):
            #If the index has hit the max
            if self.player.compound_note_index % self.x_lengths[i] == 0:
                if direct == 'left':
                    self.__change_tab_left(i)
                elif direct == 'right':
                    self.__change_tab_right(i)

    def __inst_spot(self):
        #The value that the next added instrument should have in its
        #y value
        return self.label_count * self.font_size_pix

    def add_instrument(self, instr):
        """
        Add an instrument to the window
        """
        self.label_count += 1
        #Splits instrument on / part of path to separate it
        inst_no_path = str(instr).split('/')
        #The instrument and tab
        temp = inst_no_path[-1]
        #Splits the instrument and tab so that the tab can be parsed
        instsplit = temp.split()
        #The max size of the tab
        x_length = self.max_tab_length - len(instsplit[0])
        self.x_lengths.append(self.max_tab_length - len(instsplit[0]))
        #Checks to see if the length of the tab is too large and
        #cuts it down if it is and stores the rest in the extra
        #list
        if len(instsplit[1]) > x_length:
            new_inst = instsplit[0] + ' ' + instsplit[1][:x_length]
            self.extras.append(instsplit[1][x_length:])
        else:
            new_inst = temp
            self.extras.append('')

        new_label = pyglet.text.Label(new_inst,
                                      font_name = self.font_name,
                                      font_size = 16,
                                      x = 10,
                                      y = self.height-self.__inst_spot(),
                                      color = self.colors[self.font_color])
        self.label.append(new_label)

    def __change_tab_right(self, inst_num):
        """
        Rotates the tab to the next x_length sized block
        """
        temp = None
        curr_tab = self.label[inst_num+1].text.split()

        #Checks to see if there is any extra stuff to rotate and does
        #it if necessary
        if self.extras[inst_num] != '':#> self.x_lengths[inst_num]:
            self.extras[inst_num] = self.extras[inst_num] + curr_tab[1]
            temp = self.extras[inst_num][:self.x_lengths[inst_num]]
            self.extras[inst_num] = self.extras[inst_num][self.x_lengths[inst_num]:]
        else:
            temp = curr_tab[1]

        self.label[inst_num+1].text = curr_tab[0]+' '+temp

    def __change_tab_left(self, inst_num):
        """
        Rotates the tab to the previous x_length sized block
        """
        temp = None
        curr_tab = self.label[inst_num+1].text.split()

        #Checks to see if there is any extra stuff to rotate and does
        #it if necessary
        if self.extras[inst_num] != '':
            self.extras[inst_num] = curr_tab[1] + self.extras[inst_num]
            temp = self.extras[inst_num][self.x_lengths[inst_num]:]
            self.extras[inst_num] = self.extras[inst_num][:self.x_lengths[inst_num]]
        else:
            temp = curr_tab[1]

        self.label[inst_num+1].text = curr_tab[0]+' '+temp

    def add_instruments(self, instruments):
        """
        Adds a list of instruments
        """
        for instrument in instruments:
            self.add_instrument(instrument)
