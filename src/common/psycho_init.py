def open_window(monInfo, measureFPS=True):
    """
    Open a window for the experiment
    """
    from psychopy import visual, event
    # setup the Window
    sx = int(monInfo['ResolutionX'])
    sy = int(monInfo['ResolutionY'])
    win = visual.Window(size=(sx, sy), fullscr = monInfo['RunFullScreen'],
                        screen = 0, allowGUI = False, allowStencil = False,
                        monitor = monInfo['MonitorName'],
                        color = [0, 0, 0], colorSpace = 'rgb',
                        units = 'cm', waitBlanking = True)

    print "*** Screen width= ", win.scrWidthCM, " [cm]", win.scrWidthPIX, " [px]"
    print "*** Current distance is set to", win.scrDistCM, " [cm]"
    win.setRecordFrameIntervals(True)
    if measureFPS:
        # Measure the fps
        frames = []
        waitText = visual.TextStim(
            win, "Measuring flip time for accurate timing...wait", color='Black')
        for i in range(0, 100):
            waitText.draw()
            frames.append(win.flip())
        import numpy as np
        frames = np.array(frames)
        t = np.diff(frames)
        win.measuredFlipTime = np.average(t)
        win.measuredFPS = 1.0 / win.measuredFlipTime
        #win.measuredFPS = 59.95
        text = "FlipTime= %2.2f +- %2.2f [ms].\nPress any key to continue" % (1000 * win.measuredFlipTime, 1000 * np.std(t))
        fpsText = visual.TextStim(win, text, color='Black')

        while True:
            fpsText.draw()
            keys = event.getKeys()
            win.flip()
            if keys:
                win.flip()
                break
        #print "Flip time [ms]=", win.measuredFlipTime * 1E3, "+-", np.std(t) * 1E3
        #print "FPS=", win.measuredFPS, " [Hz]"
    return win


def setup_monitor():
    """ Setup the monitor settings"""
    from psychopy import gui, core
    # store info about the experiment session
    monitorInfo = {'ResolutionX': 1280,
                   'ResolutionY': 800,
                   'RunFullScreen': True,
                   'MonitorName': 'current',
                   'RunSpeedTest': False,
                   }

    dlgMonitor = gui.DlgFromDict(
        dictionary=monitorInfo, title='MONITOR INFORMATIONS',
        order=['MonitorName', 'ResolutionX',
               'ResolutionY', 'RunFullScreen'],
        tip={'MonitorName': 'Name of the current monitor set in PsychoPy->Monitor Center',
             'ResolutionX': 'Current X resolution of the monitor',
             'ResolutionY': 'Current Y resolution of the monitor'})
    
    if not dlgMonitor.OK:
        core.quit()

    return dlgMonitor, monitorInfo


def experiment_finished(win):
    """ Wait til ESCAPE key has been pressed, then close the window """
    from psychopy import visual, event
    closeText = visual.TextStim(win, "Experiment finished, press ESC to close", color='Black')
    while True:
        closeText.draw()
        keys = event.getKeys()
        win.flip()
        if 'escape' in keys:
            break
    win.close()
        

def set_output_file(expInfo, suffix):
    """  """
    from psychopy import data
    import os
    expInfo['date'] = data.getDateStr()  # add a simple timestamp
    # setup files for saving
    # Get current save dir
    currentpath = os.getcwd()
    savedatapath = currentpath + os.path.sep + 'data' + os.path.sep + suffix + expInfo['date']

    if not os.path.isdir(savedatapath):
        # if this fails (e.g. permissions) we will get error
        os.makedirs(savedatapath)

    outputfile = savedatapath + os.path.sep + \
        'results_%s_%s_%s' % (
            expInfo['Partecipant'], expInfo['Subject code'], expInfo['date'])
    
    return outputfile


def save_experimental_settings(settings_file, expInfo, trialInfo, monitorInfo):
    import pickle
    pickle.dump([expInfo, trialInfo, monitorInfo], open(settings_file, 'w'))
