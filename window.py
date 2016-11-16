import pyglet

#upload with button click

class GarageBand(pyglet.window.Window):
        def __init__(self, func=None):
                pyglet.window.Window.__init__(self, width=500, height=500)
                self.label = [pyglet.text.Label('We are waiting...',
                                               font_name='Times New Roman',
                                               font_size=36,
                                               x=self.width//2,
                                               y=self.height//2,
                                               anchor_x='center',
                                               anchor_y='center')]

                self.label_count = 0
                self.func = func
                self.schedule = pyglet.clock.schedule_interval(
                                func = self.update,
                                interval=1/60.)

        def on_draw(self):
                self.clear()
                for label in self.label:
                        label.draw()

        def on_key_press(self, symbol, modifiers):
                pass

        def on_key_release(self, symbol, modifiers):
                #if checking key might need to be here
                self.func(pyglet.window.key.symbol_string(symbol))

        def update(self, interval):
                pass

        def set_func(self, func):
                self.func = func

        def add_inst(self, instr):
                #Add instrument and tab to labels
                pass

if __name__ == "__main__":
        window = GarageBand(func=lambda n: n)
        pyglet.app.run()
