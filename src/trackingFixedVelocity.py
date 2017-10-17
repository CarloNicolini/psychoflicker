import numpy as np
from random import randrange
from common.psycho_init import open_window, setup_monitor
from common.psycho_init import experiment_finished
from common.psycho_init import set_output_file, save_experimental_settings
from common.show_instructions import show_instructions
from psychopy import core
from common import Ball
from psychopy import visual, event

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
               'SimulationMode': False,
               'MaxAnswerTime' : 2,
               'DrawRectangles': False
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
                              'SimulationMode': 'Run the experiment with a perfect cumulative normal observer'
                          })

    if not dlg.OK:
        core.quit()  # user pressed cancel
    # nUp is the number of incorrect (or 0) responses before the staircase level increases.
    # nDown is the number of correct (or 1) responses before the staircase
    # level decreases.
    staircaseInfo = {'StepType': ['lin', 'db', 'log'],
                     'Selection': ['random', 'sequential'],
                     'TotalTrialsPerCondition': 16,

                     'Unilateral-Left speed': 5.0,
                     'Unilateral-Right speed': 5.0,
                     'Bilateral-Left speed': 2.5,
                     'Bilateral-Right speed': 2.5}

    dlgStaircase = gui.DlgFromDict(dictionary=staircaseInfo, title='Trials options',
                                   order=['StepType',
                                          'Selection',
                                          'TotalTrialsPerCondition',
                                          'Unilateral-Left speed',
                                          'Unilateral-Right speed',
                                          'Bilateral-Left speed',
                                          'Bilateral-Right speed'])

    if not dlgStaircase.OK:
        core.quit()

    outputfile = set_output_file(expInfo, 'trackingFixed_')
    save_experimental_settings(
        outputfile + '_info.pickle', expInfo, staircaseInfo, monitorInfo)
    return expInfo, staircaseInfo, outputfile, monitorInfo


def createBalls(win, nBalls, radius, boundRect, speed):
    """ Create the balls to be put in the area """
    from numpy import array
    from numpy.random import uniform
    from random import shuffle
    from common import Geometry
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
    for i in range(0, nBalls):
        startPos = array([uniform(rectanglesList[i % 4][0] + radius, rectanglesList[i % 4][2] -
                                  radius), uniform(rectanglesList[i % 4][1] + radius, rectanglesList[i % 4][3] - radius)])
        direction = Geometry.normalized(
            array([uniform(-1, 1), uniform(-1, 1)]))
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
    from numpy import array
    for i in range(0, nFrames):
        fullFrame[i] = dict()
        for ballListID, ballList in allBallsList.iteritems():
            boundingRectangle = rectangles[ballListID]
            for ball1 in ballList:
                force = array([0, 0])
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
                # print np.np.sqrt(np.dot(ball1.direction,ball1.direction))*60
                fullFrame[i][ball1] = ball1.pos()

    return fullFrame


def trackingTrial(win, experimentalInfo, ballSpeed, thisCondition, simulation=False):
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

    leftRightRectangles = [[-rectWidth - displacementX / 2.0, -rectHeight / 2.0, -displacementX / 2.0,
                            rectHeight / 2.0], [displacementX / 2.0, -rectHeight / 2.0, rectWidth + displacementX / 2.0, rectHeight / 2.0]]

    ballsLeft, rectanglesLeft = createBalls(
        win, nBallsPerRectangle, radius=ballRadius, boundRect=leftRightRectangles[0], speed=ballSpeed)
    ballsRight, rectanglesRight = createBalls(
        win, nBallsPerRectangle, radius=ballRadius, boundRect=leftRightRectangles[1], speed=ballSpeed)

    #allBallsList = { 0:ballsLowerLeft, 1:ballsLowerRight, 2:ballsUpperLeft,3:ballsUpperRight }
    allBallsList = {0: ballsLeft, 1: ballsRight}
    from numpy import array
    fixationBall = Ball(win, position=array([0.0, 0.0]), direction=array(
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
        rectanglesVisual.append(visual.Rect(win, width=(r[2] - r[0]), height=(r[3] - r[
                                1]), fillColor=None, lineColor='Red', units='cm', pos=[(r[0] + r[2]) / 2.0, (r[1] + r[3]) / 2.0]))

    # Start first part of the experiment, 2 balls blink for a certain amount
    # of time controlled by experimentalInfo['BlinkTime']
    while trialClock.getTime() < experimentalInfo['BlinkTime']:
        fixationBall.draw()
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
        win.flip()

    # Reset all colors of the balls to black and move each ball in its right
    # part of space
    for ballListID, ballList in allBallsList.iteritems():
        for ball1 in ballList:
            ball1.setColor('Black')
            ball1.draw()

    fixationBall.draw()

    win.flip()
    trialClock.reset()
    # This function pregenerates all the trajectories so that in displaying
    # them we have no slowing
    allFrames = preGenerateTrajectories(ballSpeed / win.fps(), experimentalInfo, allBallsList, leftRightRectangles,
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
        win.flip()
    event.clearEvents(eventType='keyboard')

    trialClock.reset()
    randomBall = allBallsList[whichSide][randrange(0, nBallsPerRectangle)]

    randomBall.setColor('Red')
    event.clearEvents(eventType='keyboard')

    trialClock.reset()
    responseKey = None
    response = None
    time_exceeded = False
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

        if trialClock.getTime() > experimentalInfo['MaxAnswerTime']:
            response = -1
            trialClock.reset()

        # Plot the green/red dot for 0.5 seconds
        if response != None:
            break

        if 'escape' in keys:
            win.close()
            core.quit()
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

        win.flip()

    return response


def startExperiment():
    try:
        expInfo, trialInfo, outputfile, monitorInfo = setupExperiment()
        win = open_window(monitorInfo)
        show_instructions(win, "Press spacebar to start experiment")

        # We instanciate 4 staircases, we must decide the starting values for each of them
        # The speed value is the speedValue in the for loop of staircases and is measured in [cm/s]
        # The staircase will terminate when nTrials AND nReversals have been exceeded.
        # If stepSizes was an array and has been exceeded before nTrials is
        # exceeded then the staircase will continue to reverse

        if (monitorInfo['RunSpeedTest']):
            from common.draw_test_square import draw_test_square
            draw_test_square(win)

        nTrialCounter = {}
        responses = {}
        if expInfo['Block'] == 'Unilateral':
            nTrialCounter['Unilateral-Left'] = 0
            nTrialCounter['Unilateral-Right'] = 0
            responses['Unilateral-Left'] = []
            responses['Unilateral-Right'] = []
        if expInfo['Block'] == 'Bilateral':
            nTrialCounter['Bilateral-Left'] = 0
            nTrialCounter['Bilateral-Right'] = 0
            responses['Bilateral-Left'] = []
            responses['Bilateral-Right'] = []
        if expInfo['Block'] == 'Uni+Bi':
            nTrialCounter['Unilateral-Left'] = 0
            nTrialCounter['Unilateral-Right'] = 0
            nTrialCounter['Bilateral-Left'] = 0
            nTrialCounter['Bilateral-Right'] = 0
            responses['Unilateral-Left'] = []
            responses['Unilateral-Right'] = []
            responses['Bilateral-Left'] = []
            responses['Bilateral-Right'] = []

        maxTrials = trialInfo['TotalTrialsPerCondition'] * 2
        if (expInfo['Block'] == 'Uni+Bi'):
            maxTrials *= 2

        output = open(outputfile + "_fixed_tracking.txt", 'w')
        output.write('Trial\tNTrial\tTrial Condition\tResponse\tStartTime\n')

        # Generate a list of balanced random conditions
        allConditions = []
        for n in range(0, maxTrials):
            condition = {}
            if n % 2:
                condition['Side'] = 'Left'
            else:
                condition['Side'] = 'Right'

            if expInfo['Block'] == 'Unilateral':
                condition['label'] = 'Unilateral' + '-' + condition['Side']
            if expInfo['Block'] == 'Bilateral':
                condition['label'] = 'Bilateral' + '-' + condition['Side']
            if expInfo['Block'] == 'Uni+Bi':

                if n % 4 == 0:
                    condition['label'] = 'Unilateral' + '-Right'
                if n % 4 == 1:
                    condition['label'] = 'Unilateral' + '-Left'
                if n % 4 == 2:
                    condition['label'] = 'Bilateral' + '-Right'
                if n % 4 == 3:
                    condition['label'] = 'Bilateral' + '-Left'

            allConditions.append(condition)

        # Prepare some trials with catch trials
        import copy
        for i in range(0, len(allConditions)):
            thisCondition = allConditions[i]
            if np.random.rand() < 0.5 and (thisCondition['label'].split('-')[0] == 'Bilateral'):
                thisCondition = copy.deepcopy(allConditions[i])
                thisCondition['isCatchTrial'] = True
                allConditions.append(thisCondition)

        if (trialInfo['Selection'] == 'random'):
            from random import shuffle
            shuffle(allConditions)

        for thisCondition in allConditions:
            print thisCondition

        n = 0
        expClock = core.Clock()
        trigger_received = False # Indicates whether it received the '=' symbol from the fMRI (or from the keyboard)
        while not trigger_received:
            win.flip()
            triggerKeys = event.getKeys()
            if '=' in triggerKeys:
                trigger_received = Truegit pul
                expClock.reset()
            if 'escape' in triggerKeys:
                win.close()
                core.quit()
            event.clearEvents(eventType='keyboard')

        for thisCondition in allConditions:
            t0 = expClock.getTime()
            if expInfo['Block'] == 'Unilateral':
                if nTrialCounter['Unilateral-Left'] > maxTrials and nTrialCounter['Unilateral-Right'] > maxTrials:
                    break
            if expInfo['Block'] == 'Bilateral':
                if nTrialCounter['Bilateral-Left'] > maxTrials and nTrialCounter['Bilateral-Right'] > maxTrials:
                    break
            if expInfo['Block'] == 'Uni+Bi':
                if nTrialCounter['Bilateral-Left'] > maxTrials and nTrialCounter['Bilateral-Right'] > maxTrials:
                    break
            # Extract the speed value from the input dialog for staircase for the
            # current condition
            speedValue = trialInfo[thisCondition['label'] + ' speed']
            if 'isCatchTrial' in thisCondition:
                # print "Catch trial, sarebbe ", thisCondition['Side'], "invece
                # fa dall'altra"
                if thisCondition['Side'] == 'Left':
                    thisCondition['Side'] = 'Right'
                else:
                    thisCondition['Side'] = 'Left'
                trackingTrial(
                    win, expInfo, speedValue, thisCondition, expInfo['SimulationMode'])
            else:
                # print thisCondition, speedValue
                thisResp = trackingTrial(
                    win, expInfo, speedValue, thisCondition, expInfo['SimulationMode'])
                responses[thisCondition['label']].append(thisResp)

                output.write(str(n) + "\t" + str(nTrialCounter[thisCondition['label']]) + "\t" + thisCondition['label'] + "\t" + str(int(thisResp)) + "\t" + str(t0) + "\n")
            nTrialCounter[thisCondition['label']] += 1
            n += 1
        experiment_finished(win)
    except:
        raise
        win.close()
    else:
        output.write('\n')
        # Compute accuracy, we keep just the trials from 0 to maxTrials
        accuracies = {}
        for k in responses.keys():
            accuracies[k] = float(
                sum(responses[k][0:maxTrials])) / len(responses[k][0:maxTrials])
            output.write('Accuracy ' + k + ' = ' + str(accuracies[k]) + "\n")

################################
# The experiment starts here  #
###############################
if __name__ == "__main__":
    startExperiment()
