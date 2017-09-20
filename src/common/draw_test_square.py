def draw_test_square(win, edgeLength=10):
    from psychopy import visual, event, core
    from show_instructions import show_instructions
    from Ball import Ball
    import numpy as np
    r = visual.Rect(win, edgeLength, edgeLength, units='cm')
    timer = core.Clock()
    show_instructions(win, "Measure the edges of this rectangle, it's 10x10, press SPACE when done, ESC to quit")

    b = Ball(win, position=np.array([-edgeLength / 2.0, -edgeLength / 2.0]),
             direction=np.array([1, 0]), speed=1, radius=0.1, color='Black')
    start = True
    finalTime = None
    timer.reset()
    while True:
        r.draw()
        b.draw()
        if start:
            b.move([1.0 / win.fps(), 0.0])
        if (b.pos()[0] >= edgeLength / 2.0) and start is True:
            finalTime = timer.getTime()
            break
        win.flip()

    while True:
        r.draw()
        keys = event.getKeys()
        if 'space' in keys:
            break
        if 'escape' in keys:
            win.close()
            core.quit()
        win.flip()

    show_instructions(win, "Time elapsed to run 10 cm at 1 cm/s is " +
                     str(finalTime) + " [s] press spacebar to continue, ESC to quit")