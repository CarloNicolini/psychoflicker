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
               'BallRadius': 2,
               'TrainingTrials': 0,
               'SaveVideo': False,
               'ContrastDuration': 2.0
               }

    dlg = gui.DlgFromDict(dictionary=expInfo, title='Flicker Experiment',
                          order=['Partecipant',
                                 'Subject code',
                                 'SquareEdge',
                                 'BallRadius',
                                 'TrainingTrials',
                                 ],
                          tip={
                              'Partecipant Name': 'Name of the participant',
                              'Subject code': 'Code of the subject',
                              'SquareEdge': 'Length of the virtual square edge',
                              'BallRadius': 'Radius of the balls in cm',
                              'TrainingTrials': 'Number of preparation training trials',
                          })

    if dlg.OK is False:
        core.quit()  # user pressed cancel

    # nUp is the number of incorrect (or 0) responses before the staircase level increases.
    # nDown is the number of correct (or 1) responses before the staircase
    # level decreases.
    staircaseInfo = {'StepType': ['lin', 'db', 'log'],
                     'Selection': ['random', 'sequential'],
                     'MinReversals': 6,
                     'MinTrials': 10,
                     'ContrastLeft': 0.0,
                     'ContrastRight': 0.0,
                     'StepSizes': '[0.05]',
                     'nUpLeft': 1,
                     'nUpRight': 1,
                     'nDownLeft': 1,
                     'nDownRight': 1,
                     'AverageReversals': 3}

    dlgStaircase = gui.DlgFromDict(
        dictionary=staircaseInfo, title='Staircase procedure')

    if dlgStaircase.OK is False:
        core.quit()

    outputfile = set_output_file(expInfo, 'contrast_')
    save_experimental_settings(
        outputfile + '_info.pickle', expInfo, staircaseInfo, monitorInfo)
    return expInfo, staircaseInfo, outputfile, monitorInfo


def contrastTrial(win, experimentalInfo, contrastValue, side, useSameStimuli):
    from psychopy import visual, event
    """
    Start the contrast trial
    """
    saveVideo = experimentalInfo['SaveVideo']
    edge = experimentalInfo['SquareEdge']
    # First two stimuli are on the left, second two stimuli are on the right
    positions = [np.array(
        [-edge / 2, -edge / 2]), np.array([-edge / 2, edge / 2]),
        np.array([edge / 2, -edge / 2]), np.array([edge / 2, edge / 2])]

    fixationBall = Ball(win, position=np.array([0.0, 0.0]), direction=np.array(
        [0.0, 0.0]), speed=0.0, radius=0.15, color='White')
    sameStimuliIndex = randrange(0, 4)

    noiseMaskStimuli = []
    for i in range(0, 4):
        noiseMaskStimuli.append(visual.GratingStim(
                                win, pos=positions[i],
                                tex=np.random.random_integers(
                                    0, 1, size=[1024, 1024]) * 2 - 1,
                                mask='circle',
                                size=[experimentalInfo['BallRadius'] * 2,
                                      experimentalInfo['BallRadius'] * 2]))

    # Generate the ball that has different contrast
    noiseMaskStimuli[sameStimuliIndex] = visual.GratingStim(win, pos=positions[sameStimuliIndex],
                                                            tex=np.random.random_integers(
                                                                0, 1, size=[1024, 1024]) * 2 - 1,
                                                            mask='circle',
                                                            size=[experimentalInfo['BallRadius'] * 2,
                                                                  experimentalInfo['BallRadius'] * 2])
    noiseMaskStimuli[sameStimuliIndex].contrast = contrastValue
    if useSameStimuli:
        for i in range(0, 4):
            noiseMaskStimuli[i].contrast = contrastValue

    arrows = [visual.TextStim(win, "<--", pos=[0, 0]),
              visual.TextStim(win, "-->", pos=[0, 0])]

    # Draw the arrow cue
    trialClock = core.Clock()
    trialClock.reset()

    sideIndex = (side == 'Left')
    while (trialClock.getTime() < 2.0):
        arrows[sideIndex].draw()
        if (saveVideo):
            win.getMovieFrame()
        win.flip()

    # Mostra lo stimolo di contrasti per due secondi
    totalMaskTime = experimentalInfo.get('ContrastDuration', 2.0)
    totalMaskTimeInFrames = int(round(totalMaskTime * win.measuredFPS))
    for t in range(0, totalMaskTimeInFrames):
        for i in range(0, 4):
            noiseMaskStimuli[i].draw()
        if (saveVideo):
            win.getMovieFrame()
        win.flip()

     # Get the subject response
    event.getKeys()
    trialClock = core.Clock()
    trialClock.reset()
    response = None

    while True:
        keys = event.getKeys()
        fixationBall.draw()
        if 's' in keys:
            response = (sideIndex == (sameStimuliIndex < 2))
            if useSameStimuli:
                response = True
            trialClock.reset()
            break
        if 'd' in keys:
            response = (sideIndex == (sameStimuliIndex >= 2))
            if useSameStimuli:
                response = False
            trialClock.reset()
            break
        if 'escape' in keys:
            win.close()
            core.quit()
        if (saveVideo):
            win.getMovieFrame()
        win.flip()

    if (saveVideo):
        import os
        currentpath = os.getcwd()
        savedatapath = currentpath + os.path.sep + 'data'
        outputVideo = savedatapath + os.path.sep + \
            "frames" + os.path.sep + 'contrast.png'
        print "Saving video to " + outputVideo
        win.saveMovieFrames(outputVideo)
    return response


def analyzeStaircases(stairs, nReversals):
    """
    Begin the experiment
    1. Set experimental parameters
    2. Open the window and take measurements of the refresh rate
    3. Start some training trials if needed
    4. Start the interleaved staircase experiment
    5. Save the result
    """
    from psychopy import data
    import pylab
    from numpy import average, std
    allIntensities, allResponses = [], []
    nStairs = 0
    for s in stairs.staircases:
        allIntensities.append(s.intensities)
        allResponses.append(s.data)
        nStairs = nStairs + 1

    lines, names = [], []
    for stairIndex, thisStair in enumerate(allIntensities):
        pylab.subplot(1, nStairs, stairIndex)
        rev = stairs.staircases[stairIndex].reversalIntensities
        intens = stairs.staircases[stairIndex].intensities
        pylab.title(
            'Threshold=' + str(average(rev[(len(rev) - nReversals):len(rev)])))
        pylab.plot(
            intens, 'o-', label=stairs.staircases[stairIndex].condition['label'])
        pylab.xlabel('Trial')
        pylab.grid()
        pylab.ylabel('Contrast [Michelson]')
        pylab.legend()
    pylab.show()


def startExperiment():
    try:
        expInfo, stairInfo, outputfile, monitorInfo = setupExperiment()
        win = open_window(monitorInfo, measureFPS=False)
        win.measuredFPS = 59.95
        show_instructions(win, "Press spacebar to start experiment, doing " +
                          str(expInfo['TrainingTrials']) + " training trials")

        # Convert the string of steps to a list of floats to feed to every
        # staircase
        stepSizes = [float(x)
                     for x in stairInfo['StepSizes'].replace('[', '').replace(']', '').split(',')]

        expConditions = [
            {'label': 'Right',
             'startVal': stairInfo['ContrastRight'],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpRight'],
             'nDown':stairInfo['nDownRight'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':min(stepSizes),
             'maxVal':1
             },
            {'label': 'Left',
             'startVal': stairInfo['ContrastLeft'],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpLeft'],
             'nDown':stairInfo['nDownLeft'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':min(stepSizes),
             'maxVal':1
             }]

        print "Minimum value for staircase = ", min(stepSizes)
        from psychopy import data
        stairs = data.MultiStairHandler(
            conditions=expConditions, nTrials=1, method=stairInfo['Selection'])

        if (monitorInfo['RunSpeedTest']):
            from common.draw_test_square import draw_test_square
            draw_test_square(win)

        # Do some training trials with no variation in speed
        for i in np.linspace(0.0, 2.0, expInfo['TrainingTrials']):
            contrastTrial(
                win, expInfo, contrastValue=i, side='Left', useSameStimuli=randrange(0, 2))

        show_instructions(
            win, "Finished training trials, press spacebar to begin")

        for contrast, thisCondition in stairs:
            sameStimuli = randrange(0, 100) < 25  # To present 4 equal stimuli
            thisResp = contrastTrial(win, expInfo, contrastValue=contrast,
                                     side=thisCondition['label'], useSameStimuli=sameStimuli)
            if thisResp is not None:
                stairs.addData(not thisResp)
            else:
                print "skipped"
            # save data as multiple formats for every trial
            stairs.saveAsText(outputfile)

        stairs.saveAsText(outputfile)
        stairs.saveAsPickle(outputfile)
        stairs.saveAsExcel(outputfile)
        experiment_finished(win)
    except:
        win.close()
        raise
    #analyzeStaircases(stairs, stairInfo['AverageReversals'])

################################
# The experiment starts here  #
###############################

if __name__ == "__main__":
    startExperiment()
