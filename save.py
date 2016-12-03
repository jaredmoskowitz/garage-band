
                    #Accomplishes save but if paused it will not restart
                    master = Tk()
                    e = Entry(master)
                    e.pack()
                    e.focus_set()
                    def callback():
                            self.player.save(e.get())
                            master.destroy()
                    b = Button(master, text = 'Save', width = 10, 
                               command = callback)
                    b.pack()
                    mainloop()
