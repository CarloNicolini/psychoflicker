# Choose the experiment you want

from psychopy import gui


def show_run(exp_text):
    myDlg = gui.Dlg(title="Starting")
    myDlg.addText(exp_text)
    myDlg.show()
    if not myDlg.OK:
        from psychopy import core
        core.quit()

experiments = ['TrackingStaircase', 'TrackingFixed',
               'Tracking', 'Flicker', 'FlickerFixed']
exp = {'Experiment': experiments}

dlg = gui.DlgFromDict(dictionary=exp, title='SELECT EXPERIMENT')

if exp['Experiment'] == 'TrackingStaircase':
    show_run('Starting trackingExperiment2Staircase')
    import trackingExperiment2Staircase
    trackingExperiment2Staircase.startExperiment()
elif exp['Experiment'] == 'TrackingFixed':
    show_run('Starting trackingFixedVelocity')
    import trackingFixedVelocity
    trackingFixedVelocity.startExperiment()
elif exp['Experiment'] == 'Tracking':
    show_run('Starting trackingExperiment')
    import trackingExperiment
    trackingExperiment.startExperiment()
elif exp['Experiment'] == 'Flicker':
    show_run('Starting flickerExperiment')
    import flickerExperiment
    flickerExperiment.startExperiment()
elif exp['Experiment'] == 'FlickerFixed':
    show_run('Starting flickerExperimentFixedVelocity')
    import flickerExperimentFixedVelocity
    flickerExperimentFixedVelocity.startExperiment()
