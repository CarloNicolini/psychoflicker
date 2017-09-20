import numpy as np
from random import randrange
from common.psycho_init import open_window, setup_monitor
from common.psycho_init import experiment_finished
from common.psycho_init import set_output_file, save_experimental_settings
from common.show_instructions import show_instructions

from psychopy import core
from common import Ball


def setupExperiment():
    from psychopy import gui
    """
    Setup the experimental variables with a dialog box
    """
    dlgMonitor, monitorInfo = setup_monitor()

    expInfo = {'Partecipant': 'Subj',
               'Subject code': '00',
               'SquareEdge': 6,
               'BallRadius': 0.5,
               'BlinkTime': 3,
               'TrainingTrials': 0,
               'SaveVideo': False
               }

    dlg = gui.DlgFromDict(dictionary=expInfo, title='Flicker Experiment',
                          order=['Partecipant',
                                 'Subject code',
                                 'SquareEdge',
                                 'BallRadius',
                                 'BlinkTime',
                                 'TrainingTrials',
                                 ],
                          tip={
                              'Partecipant Name': 'Name of the participant',
                              'Subject code': 'Code of the subject',
                              'SquareEdge': 'Length of the virtual square edge',
                              'BallRadius': 'Radius of the balls in cm',
                              'BlinkTime': 'Time of white/black ball blinking in seconds',
                              'TrainingTrials': 'Number of preparation training trials',
                          })

    if not dlg.OK:
        core.quit()  # user pressed cancel

    # nUp is the number of incorrect (or 0) responses before the staircase level increases.
    # nDown is the number of correct (or 1) responses before the staircase
    # level decreases.
    staircaseInfo = {'StepType': ['lin', 'db', 'log'],
                     'Selection': ['random', 'sequential'],
                     'MinReversals': 6,
                     'MinTrials': 10,
                     'FlickerFreqLeft': 10.0,
                     'FlickerFreqRight': 10.0,
                     'StepSizes': '[0.5,0.25]',
                     'nUpLeft': 1,
                     'nUpRight': 1,
                     'nDownLeft': 1,
                     'nDownRight': 1,
                     'AverageReversals': 3}

    dlgStaircase = gui.DlgFromDict(
        dictionary=staircaseInfo, title='Staircase procedure')

    if not dlgStaircase.OK:
        core.quit()

    outputfile = set_output_file(expInfo, 'flicker_')
    save_experimental_settings(
        outputfile + '_info.pickle', expInfo, staircaseInfo, monitorInfo)

    return expInfo, staircaseInfo, outputfile, monitorInfo


def flickerTrial(win, experimentalInfo, flickerFreq, side, useOddBall):
    from psychopy import visual, event
    """
    Start the tracking trial
    """
    # Generate the 4 balls as list
    balls = []
    edge = experimentalInfo['SquareEdge']
    # First two balls are left, second two balls are right
    positions = [np.array(
        [-edge / 2, -edge / 2]), np.array([-edge / 2, edge / 2]),
        np.array([edge / 2, -edge / 2]), np.array([edge / 2, edge / 2])]
    for i in range(0, 4):
        balls.append(Ball(win, position=positions[i], direction=np.array(
            [0, 0]), speed=0, radius=experimentalInfo['BallRadius'], color='Black'))

    fixationBall = Ball(win, position=np.array([0.0, 0.0]), direction=np.array(
        [0.0, 0.0]), speed=0.0, radius=0.15, color='White')
    oddBallIndex = randrange(0, 4)
    oddBalls = [balls[oddBallIndex]]

    noiseMaskStimuli = []
    for i in range(0, 4):
        noiseMaskStimuli.append(visual.GratingStim(win, pos=positions[i], units='cm',tex=np.random.rand(
            256, 256) * 2.0 - 1.0, mask='circle', size=[experimentalInfo['BallRadius'] * 2, experimentalInfo['BallRadius'] * 2]))

    arrows = [visual.TextStim(win, "<--", pos=[0, 0]),
              visual.TextStim(win, "-->", pos=[0, 0])]
    # Initialize a color for the balls
    for ball in balls:
        ball.setColor('Black')
        if useOddBall:
            for oddBall in oddBalls:
                oddBall.setColor('White')

    # Draw the arrow cue
    trialClock = core.Clock()
    trialClock.reset()

    sideIndex = side == 'Left'
    while (trialClock.getTime() < 2.0):
        arrows[sideIndex].draw()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    totalMaskTime = 0.350  # seconds
    totalMaskTimeInFrames = int(round(totalMaskTime * win.measuredFPS))
    for t in range(0, totalMaskTimeInFrames):
        for i in range(0, 4):
            noiseMaskStimuli[i].draw()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    # Here instead of using timers we precompute the number of frames to display for the stimuli, so
    # that the calls to timers are avoided and the program is faster between
    # two flips
    totStimFrames = int(round(experimentalInfo['BlinkTime'] * win.measuredFPS))
    totBlinkFrames = int(round(1.0 / flickerFreq * win.measuredFPS))

    blinkFrame, totBlinks = 0, 0
    times = [None] * totStimFrames
    switchIndices = []
    for t in range(0, totStimFrames):
        fixationBall.draw()
        blinkFrame = blinkFrame + 1
        oldTotBlinks = totBlinks
        if (blinkFrame >= totBlinkFrames):
            blinkFrame = 0
            totBlinks = totBlinks + 1
            if (oldTotBlinks < totBlinks):
                switchIndices.append(t)
                if (totBlinks % 2):
                    for ball in balls:
                        ball.setColor('White')
                    if useOddBall:
                        for oddBall in oddBalls:
                            oddBall.setColor('Black')
                else:
                    for ball in balls:
                        ball.setColor('Black')
                    if useOddBall:
                        for oddBall in oddBalls:
                            oddBall.setColor('White')
        for ball in balls:
            ball.draw()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        times[t] = win.flip()

    totalMaskTimeInFrames = int(round(totalMaskTime * win.measuredFPS))
    for t in range(0, totalMaskTimeInFrames):
        for i in range(0, 4):
            noiseMaskStimuli[i].draw()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    times = np.array(times)
    # switchIndices=np.array(switchIndices)
    # switchTimes=np.diff(times[switchIndices])
    # print "Average switch times",np.average(switchTimes),"corresponding to ",1.0/np.average(switchTimes)," [Hz]"
    # print "Average inversion times
    # error=",np.average(switchTimes-1.0/flickerFreq)*1000,"[ms]"

    # Get the subject response
    event.getKeys()
    trialClock = core.Clock()
    trialClock.reset()
    response = None
    while True:
        keys = event.getKeys()
        fixationBall.draw()
        if 's' in keys:
            response = (sideIndex == (oddBallIndex < 2))
            trialClock.reset()
            break
        if 'd' in keys:
            response = (sideIndex == (oddBallIndex >= 2))
            trialClock.reset()
            break
        if 'escape' in keys:
            win.close()
            core.quit()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    if (experimentalInfo['SaveVideo']):
        import os
        currentpath = os.getcwd()
        savedatapath = currentpath + os.path.sep + 'data'
        outputVideo = savedatapath + os.path.sep + \
            "frames" + os.path.sep + 'Flicker.png'
        print "Saving video to " + outputVideo
        win.saveMovieFrames(outputVideo)
    return response


def startExperiment():
    """
    Begin the experiment
    1. Set experimental parameters
    2. Open the window and take measurements of the refresh rate
    3. Start some training trials if needed
    4. Start the interleaved staircase experiment
    5. Save the result
    """
    try:
        expInfo, stairInfo, outputfile, monitorInfo = setupExperiment()
    except:
        raise
    try:
        win = open_window(monitorInfo)
        show_instructions(win, "Press spacebar to start experiment, doing " +
                          str(expInfo['TrainingTrials']) + " training trials")

        # Convert the string of steps to a list of floats to feed to every
        # staircase
        stepSizes = [float(x)
                     for x in stairInfo['StepSizes'].replace('[', '').replace(']', '').split(',')]

        expConditions = [
            {'label': 'Right',
             'startVal': stairInfo['FlickerFreqRight'],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpRight'],
             'nDown':stairInfo['nDownRight'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':min(stepSizes)
             },
            {'label': 'Left',
             'startVal': stairInfo['FlickerFreqLeft'],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpLeft'],
             'nDown':stairInfo['nDownLeft'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':min(stepSizes)
             }]
        from psychopy import data
        stairs = data.MultiStairHandler(
            conditions=expConditions, nTrials=1, method=stairInfo['Selection'])

        if (monitorInfo['RunSpeedTest']):
            from common.draw_test_square import draw_test_square
            draw_test_square(win)

        # Do some training trials with no variation in speed
        for i in range(0, int(expInfo['TrainingTrials'])):
            flickerTrial(
                win, expInfo, flickerFreq=1, side='Left', useOddBall=True)

        show_instructions(
            win, "Finished training trials, press spacebar to begin")
        for flickerFreq, thisCondition in stairs:
            thisResp = flickerTrial(win, expInfo, flickerFreq,
                                    side=thisCondition['label'], useOddBall=True)
            if thisResp is not None:
                stairs.addData(not thisResp)
            stairs.saveAsText(outputfile)

        stairs.saveAsText(outputfile)
        stairs.saveAsPickle(outputfile)
        stairs.saveAsExcel(outputfile)
        experiment_finished(win)
    except:
        stairs.saveAsText(outputfile)
        stairs.saveAsPickle(outputfile)
        stairs.saveAsExcel(outputfile)
        win.close()
        raise
    #analyzeStaircases(stairs, stairInfo['AverageReversals'])

################################
# The experiment starts here  #
###############################

if __name__ == "__main__":
    startExperiment()
