import pyglet

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

                self.label_count = 0
                self.font_size_pix = 16
                self.schedule = pyglet.clock.schedule_interval(
                                func = self.update,
                                interval=1/60.)
                self.instruments = list()
                self.current_index = 0
                self.player = player
                self.add_instruments(self.player.instruments)

        def on_draw(self):
                """
                Draws all the instruments and whatever else to the window
                """
                self.clear()
                for label in self.label:
                        label.draw()

        def on_key_press(self, symbol, modifiers):
                pass

        def on_key_release(self, symbol, modifiers):
                #if checking key might need to be here
                string = pyglet.window.key.symbol_string(symbol).strip('_').upper()

                if string.isdigit():
                    self.player.write_note(self.player.instruments[self.current_index], float(string))
                elif string == "DOWN":
                    self.current_index = (self.current_index + 1)%len(self.player.instruments)
                elif string == "UP":
                    self.current_index = self.current_index - 1
                elif string == "SPACE":
                    if self.player.is_paused:
                        self.player.resume()
                    else:
                        self.player.pause()
                elif string == "T":
                    self.player.stop()
                elif string == "S":
                    self.player.save("newmusic.txt")

        def update(self, interval):
                """
                Necessary function for the window to redraw itself
                """
                if (self.player.dirty):
                    self.label[1:] = []
                    self.label_count = 0
                    self.add_instruments(self.player.instruments)
                    self.player.dirty = False

        def __inst_spot(self):
                return self.label_count * self.font_size_pix

        def add_instrument(self, instr):
                """
                Add an instrument to the window
                """
                self.label_count += 1
                new_label = pyglet.text.Label(str(instr),
                                              font_name = 'Times New Roman',
                                              font_size = 12,
                                              x=10,
                                              y=self.height-self.__inst_spot())
                self.label.append(new_label)

        def add_instruments(self, instruments):
                for instrument in instruments:
                        self.add_instrument(instrument)

if __name__ == "__main__":
        window = GarageBand(func=lambda n: n)
        inst = Inst("Source1", "Tab1")
        inst2 = Inst("Source2", "Tab2")
        window.add_inst(inst)
        window.add_inst(inst2)
        pyglet.app.run()
