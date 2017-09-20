def show_instructions(win, instructionsText):
    from psychopy import visual, event, core
    """
    Print some instructions before the experiment starts
    """
    instructionsText = visual.TextStim(
        win, text=instructionsText, pos=[0, 0], color=[-1, -1, -1])
    while True:
        keys = event.getKeys()
        instructionsText.draw()
        if 'space' in keys:
            break
        if 'escape' in keys:
            win.close()
            core.quit()
        win.flip()
    return