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
               'SaveVideo': False}

    dlgExpInfo = gui.DlgFromDict(dictionary=expInfo, title='Flicker Experiment',
                                 order=['Partecipant',
                                        'Subject code',
                                        'SquareEdge',
                                        'BallRadius',
                                        'BlinkTime',
                                        'TrainingTrials'],
                                 tip={
                                     'Partecipant': 'Name of the participant',
                                     'Subject code': 'Code of the subject',
                                     'SquareEdge': 'Length of the virtual square edge [cm]',
                                     'BallRadius': 'Radius of the balls [cm',
                                     'BlinkTime': 'Time of white/black ball blinking seconds',
                                     'TrainingTrials': 'Number of preparation training trials',
                                 })

    if not dlgExpInfo.OK:
        core.quit()  # user pressed cancel

    trialInfo = {'Selection': ['random', 'sequential', 'fullRandom'],
                 'TotalTrialsPerCondition': 2,
                 'FlickerFreqLeft': 10.0,
                 'FlickerFreqRight': 10.0}
    # Initialize a panel to ask user some trial informations
    dlgTrial = gui.DlgFromDict(dictionary=trialInfo, title='Trial variable',
                               tip={'Selection': '\'sequential\' obviously presents the conditions in the order they appear in the list.\
                               \'random\' will result in a shuffle of the conditions on each repeat, but all conditions  occur once \
                               before the second repeat etc. \'fullRandom\' fully randomises the trials across repeats as well, \
                               which means you could potentially run all trials of \one condition before any trial of another.'})

    if not dlgTrial.OK:
        core.quit()

    outputfile = set_output_file(expInfo, 'flickerFixed_')
    save_experimental_settings(
        outputfile + '_info.pickle', expInfo, trialInfo, monitorInfo)
    return expInfo, trialInfo, outputfile, monitorInfo


def flickerTrial(win, experimentalInfo, flickerFreq, side, useOddBall):
    from psychopy import visual, event
    # Generate the 4 balls as a list
    balls = []
    edge = experimentalInfo['SquareEdge']
    # First two balls are left, second two balls are right
    positions = [np.array([-edge / 2, -edge / 2]), np.array([-edge / 2, edge / 2]),
                 np.array([edge / 2, -edge / 2]), np.array([edge / 2, edge / 2])]
    for i in range(0, 4):
        balls.append(Ball(win, position=positions[i], direction=np.array(
            [0, 0]), speed=0, radius=experimentalInfo['BallRadius'], color='Black'))

    fixationBall = Ball(win, position=np.array([0.0, 0.0]), direction=np.array(
        [0.0, 0.0]), speed=0.0, radius=0.15, color='White')
    oddBallIndex = randrange(0, 4)
    oddBalls = [balls[oddBallIndex]]

    noiseMaskStimuli = []
    from numpy import random
    for i in range(0, 4):
        noiseMaskStimuli.append(visual.GratingStim(win, pos=positions[i], units='cm', tex=random.rand(
            256, 256) * 2.0 - 1.0, mask='circle', size=[experimentalInfo['BallRadius'] * 2, experimentalInfo['BallRadius'] * 2]))

    arrows = [visual.TextStim(
        win, "<--", pos=[0, 0]), visual.TextStim(win, "-->", pos=[0, 0])]
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
        expInfo, trialInfo, outputfile, monitorInfo = setupExperiment()
        win = open_window(monitorInfo)
        show_instructions(win, "Press spacebar to start experiment, doing " +
                          str(expInfo['TrainingTrials']) + " training trials")
        # Setup the experimental trials conditions
        expConditions = [{'label': 'Right', 'flickerFreq': trialInfo['FlickerFreqRight']}, {
            'label': 'Left', 'flickerFreq': trialInfo['FlickerFreqLeft']}]

        # Import the data module for the TrialHandler facility
        from psychopy import data
        trials = data.TrialHandler(
            expConditions, nReps=int(trialInfo['TotalTrialsPerCondition']))
        # Start drawing the test square
        if (monitorInfo['RunSpeedTest']):
            from common.draw_test_square import draw_test_square
            draw_test_square(win)
        # Do some training trials with no variation in speed
        for i in range(0, int(expInfo['TrainingTrials'])):
            flickerTrial(
                win, expInfo, flickerFreq=1, side='Left', useOddBall=True)

        # Done with the training trials, now show some instructions and wait the
        # user to press spacebar to continue
        show_instructions(
            win, "Finished training trials, press spacebar to begin")

        # Now starts with the true experiment
        # Trials are being picked from the trials structure rather than the staircase structure
        # since they all have fixed speed
        for thisTrial in trials:
            thisResp = flickerTrial(
                win, expInfo, thisTrial['flickerFreq'], side=thisTrial['label'], useOddBall=True)
            if thisResp is not None:
                trials.addData('Response', thisResp)

            trials.saveAsText(outputfile)

        # Save data as multiple formats
        trials.saveAsText(outputfile)
        trials.saveAsPickle(outputfile)
        trials.saveAsExcel(outputfile)
        experiment_finished(win)
    except:
        trials.saveAsText(outputfile)
        trials.saveAsPickle(outputfile)
        trials.saveAsExcel(outputfile)
        win.close()
        raise

################################
# The experiment starts here  #
###############################
if __name__ == "__main__":
    startExperiment()
