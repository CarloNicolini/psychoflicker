import numpy as np
from random import randrange
from common.psycho_init import open_window, setup_monitor
from common.psycho_init import experiment_finished
from common.psycho_init import set_output_file, save_experimental_settings
from common.show_instructions import show_instructions
import pandas as pd
from psychopy import core
from common import Ball
from common import perfectObserver

def setupExperiment():
    from psychopy import gui
    """
    Setup the experimental variables with a dialog box
    """
    dlgMonitor, monitorInfo = setup_monitor()

    expInfo = {'Partecipant': 'Subj',
               'Block': ['Unilateral', 'Bilateral', 'Uni+Bi'],
               'Subject code': '00',
               'NumBalls': 4,
               'RectWidth': 6,
               'RectHeight': 6,
               'BallRadius': 0.25,
               'Duration': 2,
               'BlinkTime': 1,
               'TrainingTrials': 0,
               'SimulationMode': False,
               'DrawRectangles': False,
               'SaveVideo': False
               }

    dlg = gui.DlgFromDict(dictionary=expInfo, title='Tracking Experiment',
                          order=['Partecipant',
                                 'Subject code',
                                 'Block',
                                 'RectWidth',
                                 'RectHeight',
                                 'BallRadius',
                                 'Duration',
                                 'BlinkTime',
                                 'TrainingTrials',
                                 'NumBalls',
                                 'SimulationMode'],
                          tip={
                              'Partecipant Name': 'Name of the participant',
                              'Subject code': 'Code of the subject',
                              'RectWidth': 'Width in cm of the left or right rectangle',
                              'RectHeight': 'Height in cm of the left or right rectangle',
                              'BallRadius': 'Radius of the balls in cm',
                              'Duration': 'Duration of the stimulus in seconds',
                              'BlinkTime': 'Time of white/black ball blinking in seconds',
                              'TrainingTrials': 'Number of preparation training trials',
                              'SimulationMode': 'Run the experiment with a perfect cumulative normal observer'
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
                     'SpeedUniLeft': '[5.0,6.0]',
                     'SpeedUniRight': '[5.0,6.0]',
                     'SpeedBiLeft': '[2.5,4.0]',
                     'SpeedBiRight': '[2.5,4.0]',
                     'StepSizes': '[0.5,0.25]',
                     'nUpUniLeft': 1,
                     'nUpUniRight': 1,
                     'nUpBiLeft': 1,
                     'nUpBiRight': 1,
                     'nDownUniLeft': 1,
                     'nDownUniRight': 1,
                     'nDownBiLeft': 1,
                     'nDownBiRight': 1,
                     'AverageReversals': 3}

    dlgStaircase = gui.DlgFromDict(
        dictionary=staircaseInfo, title='Staircase procedure')

    if not dlgStaircase.OK:
        core.quit()

    outputfile = set_output_file(expInfo, 'trackingStaircase_')
    save_experimental_settings(
        outputfile + '_info.pickle', expInfo, staircaseInfo, monitorInfo)
    return expInfo, staircaseInfo, outputfile, monitorInfo


def createBalls(win, nBalls, radius, boundRect, speed):
    """ Create the balls to be put in the area """
    halfX = (boundRect[0] + boundRect[2]) / 2.0
    halfY = (boundRect[1] + boundRect[3]) / 2.0
    # The four rectangles that build the main rectangle
    rectanglesList = []
    rectanglesList.append([boundRect[0], boundRect[1], halfX, halfY])
    rectanglesList.append([halfX, boundRect[1], boundRect[2], halfY])
    rectanglesList.append([boundRect[0], halfY, halfX, boundRect[3]])
    rectanglesList.append([halfX, halfY, boundRect[2], boundRect[3]])

    # Generate the balls in the
    balls = []
    from random import shuffle
    from numpy.random import uniform
    from common import Geometry
    for i in range(0, nBalls):
        startPos = np.array(
            [uniform(
                rectanglesList[
                    i % 4][0] + radius, rectanglesList[i % 4][2] - radius),
             uniform(rectanglesList[i % 4][1] + radius, rectanglesList[i % 4][3] - radius)])
        direction = Geometry.normalized(
            np.array([uniform(-1, 1), uniform(-1, 1)]))
        ball = Ball(win, position=startPos, direction=direction,
                    speed=speed, radius=radius, color='Black')
        balls.append(ball)

    shuffle(balls)
    return balls, rectanglesList


def preGenerateTrajectories(ballSpeed, expInfo, allBallsList, rectangles, repulsionStrength, edgerepulsionStrength, centerAttraction):
    """
    Precompute the trajectories of points
    """
    trajClock = core.Clock()
    trajClock.reset()
    nFrames = int(expInfo['Duration'] / (1.0 / 60.0))
    fullFrame = [None] * nFrames  # preallocate space for the list
    from common import Geometry
    for i in range(0, nFrames):
        fullFrame[i] = dict()
        for ballListID, ballList in allBallsList.iteritems():
            boundingRectangle = rectangles[ballListID]
            for ball1 in ballList:
                force = np.array([0, 0])
                for ball2 in ballList:
                    if (ball1 == ball2):
                        continue
                    # balls collide
                    delta = ((ball1.pos() - ball2.pos()))
                    dist2 = ((delta ** 2).sum())
                    force = force + repulsionStrength * \
                        (ball1.radius * ball2.radius) * delta / (dist2 * dist2)

                # Repulsion to borders
                force[0] = force[0] + edgerepulsionStrength / \
                    ((boundingRectangle[0] - ball1.pos()[0]) ** 2)
                force[0] = force[0] - edgerepulsionStrength / \
                    ((boundingRectangle[2] - ball1.pos()[0]) ** 2)

                force[1] = force[1] + edgerepulsionStrength / \
                    ((boundingRectangle[1] - ball1.pos()[1]) ** 2)
                force[1] = force[1] - edgerepulsionStrength / \
                    ((boundingRectangle[3] - ball1.pos()[1]) ** 2)

                # Add a little attraction to the center of boundingRectangle
                dispFromCenter = Geometry.rectangleCenter(boundingRectangle)
                force = force - (ball1.pos() - dispFromCenter)

                ball1.direction = ball1.direction + centerAttraction * force

                # Renormalize direction with correct speed
                ball1.direction = Geometry.normalized(
                    ball1.direction) * ballSpeed

                # Move the ball in the computed direction and finally draw it
                ball1.move(ball1.direction)
                # if (i==1): #print displacement for debug purpose
                #    print np.sqrt(np.dot(ball1.direction,ball1.direction))*60
                fullFrame[i][ball1] = ball1.pos()

    return fullFrame


def trackingTrial(win, experimentalInfo, ballSpeed, thisCondition, simulation=False, isCatchTrial=0):
    if simulation:
        return perfectObserver(obs_mean=3, obs_std=0.1, intensity=ballSpeed)
    from psychopy import visual, event
    """
    Start the tracking trial
    1) Generate random balls
    2) Generate the central white fixation dot
    3) Start blinking 2 balls in the left or right zone, for unilateral, in both zones for bilateral
    4) Move the balls in random directions, bouncing on walls and on theirselves
    """
    # Generate a list of 4 balls on left side for unilateral condition
    trialClock = core.Clock()

    rectWidth, rectHeight = experimentalInfo[
        'RectWidth'], experimentalInfo['RectHeight']
    displacementX = 4  # 1 cm central displacement
    nBallsPerRectangle = experimentalInfo['NumBalls']
    ballRadius = experimentalInfo['BallRadius']

    leftRightRectangles = [
        [-rectWidth - displacementX / 2.0, -rectHeight / 2.0,
            -displacementX / 2.0, rectHeight / 2.0],
        [displacementX / 2.0, -rectHeight / 2.0, rectWidth + displacementX / 2.0, rectHeight / 2.0]]

    ballsLeft, rectanglesLeft = createBalls(
        win, nBallsPerRectangle, radius=ballRadius, boundRect=leftRightRectangles[0], speed=ballSpeed)
    ballsRight, rectanglesRight = createBalls(
        win, nBallsPerRectangle, radius=ballRadius, boundRect=leftRightRectangles[1], speed=ballSpeed)

    #allBallsList = { 0:ballsLowerLeft, 1:ballsLowerRight, 2:ballsUpperLeft,3:ballsUpperRight }
    allBallsList = {0: ballsLeft, 1: ballsRight}

    fixationBall = Ball(win, position=np.array([0.0, 0.0]), direction=np.array(
        [0.0, 0.0]), speed=0.0, radius=0.10, color='White')
    trialClock.reset()
    blinkingBalls = list()

    whichSide = None
    if thisCondition['Side'] == 'Left':
        whichSide = 0
    if thisCondition['Side'] == 'Right':
        whichSide = 1

    runMode = None
    if thisCondition['label'].split('-')[0] == 'Unilateral':
        runMode = 0
    if thisCondition['label'].split('-')[0] == 'Bilateral':
        runMode = 1

    runModes = {0: 'Unilateral', 1: 'Bilateral'}

    if runModes[runMode] == 'Unilateral':
        blinkingBalls = [
            allBallsList[whichSide][0],
            allBallsList[whichSide][1]
        ]
    if runModes[runMode] == 'Bilateral':
        blinkingBalls = [allBallsList[0][0],
                         allBallsList[0][1],
                         allBallsList[1][0],
                         allBallsList[1][1]
                         ]

    if runModes[runMode] != 'Unilateral' and runModes[runMode] != 'Bilateral':
        raise Exception("Run mode must be \"Unilateral\" or \"Bilateral\"")

    blinkTimer = core.Clock()
    blinkInteger = 0
    rectanglesVisual = []
    for r in rectanglesLeft + rectanglesRight:
        rectanglesVisual.append(visual.Rect(win, width=(
            r[2] - r[0]), height=(r[3] - r[1]), fillColor=None, lineColor='Red', units='cm',pos=[(r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0]))

    # Start first part of the experiment, 2 balls blink for a certain amount
    # of time controlled by experimentalInfo['BlinkTime']
    if isCatchTrial==1:
        catchText = visual.TextStim(win, "Catch 25% trial speed=" + str(ballSpeed), color='Red', pos=[0,0])
    elif isCatchTrial==2:
        catchText = visual.TextStim(win, "Catch 50% trial speed=" + str(ballSpeed), color='Blue', pos=[0,0])
    while trialClock.getTime() < experimentalInfo['BlinkTime']:
        fixationBall.draw()
        if isCatchTrial:
            catchText.draw()
        # speedText.draw()
        if experimentalInfo['DrawRectangles']:
            for r in rectanglesVisual:
                r.draw()
        for ballListID, ballList in allBallsList.iteritems():
            for ball1 in ballList:
                ball1.draw()

        if (blinkTimer.getTime() > 0.125):
            blinkInteger = blinkInteger + 1
            blinkTimer.reset()
        if (blinkInteger % 2):
            for blinkBall in blinkingBalls:
                blinkBall.setColor('White')
        else:
            for blinkBall in blinkingBalls:
                blinkBall.setColor('Black')
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    # Reset all colors of the balls to black and move each ball in its right
    # part of space
    for ballListID, ballList in allBallsList.iteritems():
        for ball1 in ballList:
            ball1.setColor('Black')
            ball1.draw()

    fixationBall.draw()
    if (experimentalInfo['SaveVideo']):
        win.getMovieFrame()

    win.flip()
    trialClock.reset()
    # This function pregenerates all the trajectories so that in displaying
    # them we have no slowing
    allFrames = preGenerateTrajectories(
        ballSpeed /
        win.fps(), experimentalInfo, allBallsList, leftRightRectangles,
        repulsionStrength=2000.0 * ballSpeed, edgerepulsionStrength=10.0 * ballSpeed, centerAttraction=0.0001)

    trialClock.reset()
    for balls in allFrames:
        for ball, pos in balls.iteritems():
            ball.setPos(pos)
            ball.draw()
        # speedText.draw()
        if experimentalInfo['DrawRectangles']:
            for r in rectanglesVisual:
                r.draw()
        fixationBall.draw()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()

        win.flip()
    event.clearEvents(eventType='keyboard')

    trialClock.reset()
    randomBall = allBallsList[whichSide][randrange(0, nBallsPerRectangle)]

    randomBall.setColor('Red')
    event.clearEvents(eventType='keyboard')

    trialClock.reset()
    responseKey = None
    response = None
    while True:
        keys = event.getKeys()
        fixationBall.draw()
        for ballListID, ballList in allBallsList.iteritems():
            for ball1 in ballList:
                ball1.draw()
        randomBall.draw()

        if 's' in keys:
            responseKey = True
            response = responseKey == (randomBall in blinkingBalls)
            trialClock.reset()

        if 'd' in keys:
            responseKey = False
            response = responseKey == (randomBall in blinkingBalls)
            trialClock.reset()

        # Plot the green/red dot for 0.5 seconds
        if response is not None:
            break

        if 'escape' in keys:
            win.close()
            core.quit()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    if response is True:
        fixationBall.setColor('Green')
    if response is False:
        fixationBall.setColor('Red')

    trialClock.reset()
    while trialClock.getTime() < 0.4:
        keys = event.getKeys()
        fixationBall.draw()
        for ballListID, ballList in allBallsList.iteritems():
            for ball1 in ballList:
                ball1.draw()
        randomBall.draw()
        if (experimentalInfo['SaveVideo']):
            win.getMovieFrame()
        win.flip()

    if (experimentalInfo['SaveVideo']):
        import os
        currentpath = os.getcwd()
        savedatapath = currentpath + os.path.sep + 'data'
        outputVideo = savedatapath + os.path.sep + \
            "frames" + os.path.sep + 'Tracking.png'
        print "Saving video to " + outputVideo
        win.saveMovieFrames(outputVideo)

    return response


def startExperiment():
    try:
        expInfo, stairInfo, outputfile, monitorInfo = setupExperiment()
        win = open_window(monitorInfo)
        show_instructions(win, "Press spacebar to start experiment, doing " +
                          str(expInfo['TrainingTrials']) + " training trials")

        # We instanciate 4 staircases, we must decide the starting values for each of them
        # The speed value is the speedValue in the for loop of staircases and is measured in [cm/s]
        # The staircase will terminate when nTrials AND nReversals have been exceeded.
        # If stepSizes was an array and has been exceeded before nTrials is
        # exceeded then the staircase will continue to reverse

        # Convert the string of steps to a list of floats to feed to every
        # staircase
        stepSizes = [float(x)
                     for x in stairInfo['StepSizes'].replace('[', '').replace(']', '').split(',')]

        # Convert the initial velocities of the staircases
        SpeedBiRight = [float(x)
                        for x in stairInfo['SpeedBiRight'].replace('[', '').replace(']', '').split(',')]
        SpeedBiLeft = [float(x)
                       for x in stairInfo['SpeedBiLeft'].replace('[', '').replace(']', '').split(',')]
        SpeedUniRight = [float(x)
                         for x in stairInfo['SpeedUniRight'].replace('[', '').replace(']', '').split(',')]
        SpeedUniLeft = [float(x)
                        for x in stairInfo['SpeedUniLeft'].replace('[', '').replace(']', '').split(',')]

        conditionsBilateral = [
            {'label': 'Bilateral-Right_0',
             'Side': 'Right',
             'startVal': SpeedBiRight[0],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpBiRight'],
             'nDown':stairInfo['nDownBiRight'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             },

            {'label': 'Bilateral-Left_0',
             'Side': 'Left',
             'startVal': SpeedBiLeft[0],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpBiLeft'],
             'nDown':stairInfo['nDownBiLeft'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             },

            {'label': 'Bilateral-Right_1',
             'Side': 'Right',
             'startVal': SpeedBiRight[1],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpBiRight'],
             'nDown':stairInfo['nDownBiRight'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             },

            {'label': 'Bilateral-Left_1',
             'Side': 'Left',
             'startVal': SpeedBiLeft[1],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpBiLeft'],
             'nDown':stairInfo['nDownBiLeft'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             }
        ]
        ########## CONDITIONS UNILATERAL ##########
        conditionsUnilateral = [
            {'label': 'Unilateral-Right_0',
             'Side': 'Right',
             'startVal': SpeedUniRight[0],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpUniRight'],
             'nDown':stairInfo['nDownUniRight'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             },

            {'label': 'Unilateral-Left_0',
             'Side': 'Left',
             'startVal': SpeedUniLeft[0],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpUniLeft'],
             'nDown':stairInfo['nDownUniLeft'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             },

            {'label': 'Unilateral-Right_1',
             'Side': 'Right',
             'startVal': SpeedUniRight[1],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpUniRight'],
             'nDown':stairInfo['nDownUniRight'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             },

            {'label': 'Unilateral-Left_1',
             'Side': 'Left',
             'startVal': SpeedUniLeft[1],
             'method':'2AFC',
             'stepType':stairInfo['StepType'],
             'stepSizes':stepSizes,
             'nUp':stairInfo['nUpUniLeft'],
             'nDown':stairInfo['nDownUniLeft'],
             'nTrials':stairInfo['MinTrials'],
             'nReversals':stairInfo['MinReversals'],
             'minVal':0
             }
        ]

        conditions = None
        if expInfo['Block'] == 'Unilateral':
            conditions = conditionsUnilateral
        if expInfo['Block'] == 'Bilateral':
            conditions = conditionsBilateral
        if expInfo['Block'] == 'Uni+Bi':
            conditions = conditionsUnilateral + conditionsBilateral
        from psychopy import data
        stairs = data.MultiStairHandler(
            conditions=conditions, nTrials=2, method=stairInfo['Selection'])

        if (monitorInfo['RunSpeedTest']):
            from common.draw_test_square import draw_test_square
            draw_test_square(win)
        # Do some training trials with no variation in speed
        for i in range(0, int(expInfo['TrainingTrials'])):
            speedValue = 1.25 * (i + 1)
            trackingTrial(win, expInfo, speedValue, conditions[randrange(0, 2)])

        show_instructions(
            win, "Finished training trials, press spacebar to begin")
        velocityConditions = {}
        velocityConditions['Left'] = []
        velocityConditions['Right'] = []
        # Start of the trial loop
        # We save the last speed used for every side of stimulus presentation
        nTrial = 0
        import copy
        # Has to initialize the first trial
        speedValue, thisCondition = stairs.next()
        nCatchTrials = 0
        nValidTrials = 0
        dfrows = [] # Collects all trials included catch trials
        print thisCondition
        while True: # Using while True is the correct way to insert catch trials
            velocityConditions[thisCondition['Side']].append(speedValue)
            # print thisCondition['Side'], speedValue
            # Catch trial presentato al 25% di probabilita
            if np.random.rand() < 0.25 and nTrial > 2:
                nCatchTrials += 1
                catchCondition = copy.deepcopy(thisCondition)
                if thisCondition['Side'] == 'Left':
                    catchCondition['Side'] = 'Left'
                    catchSpeedValue = velocityConditions['Right'][-1]
                else:
                    catchCondition['Side'] = 'Right'
                    catchSpeedValue = velocityConditions['Left'][-1]
                catchResp = trackingTrial(win, expInfo, catchSpeedValue, catchCondition, simulation=expInfo['SimulationMode'], isCatchTrial=0) #doesn't print message
                dfrows.append({'label':catchCondition['label'], 'Side':catchCondition['Side'], 'CatchCondition':1, 'Speed':speedValue, 'Response':int(not catchResp)})
            else:
                thisResp = trackingTrial(win, expInfo, speedValue, thisCondition, simulation=expInfo['SimulationMode'],isCatchTrial=0)
                dfrows.append({'label':thisCondition['label'], 'Side':thisCondition['Side'], 'CatchCondition':0, 'Speed':speedValue, 'Response':int(not thisResp)})
                if thisResp is not None:
                    stairs.addResponse(int(not thisResp))
                    nValidTrials += 1
                    try:
                        speedValue, thisCondition = stairs.next()
                    except StopIteration:
                        break
                else:
                    raise
            # Increase the trial counter and save the temporary results
            nTrial = nTrial + 1
            stairs.saveAsText(outputfile)
            stairs.saveAsPickle(outputfile)
            df = pd.DataFrame(dfrows) # this holds all trials in raw mode
        stairs.saveAsExcel(outputfile)
        experiment_finished(win)
        df.to_excel(outputfile+'_trials_summary.xlsx')
    except:
        # If the experiments stops before a default response is inserted
        stairs.addResponse(0)
        stairs.saveAsExcel(outputfile)
        df.to_excel(outputfile+'_trials_summary.xlsx')
        win.close()
        raise

    #analyzeStaircases(stairs, stairInfo['AverageReversals'])

################################
# The experiment starts here  #
###############################
if __name__ == "__main__":
    startExperiment()
