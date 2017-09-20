def perfectObserver(obs_mean, obs_std, intensity, guessRate=0, lapseRate=0):
    import numpy as np
    from scipy.special import erf
    decision = np.random.rand()
    observer  = guessRate+(1-guessRate-lapseRate)*(0.5*(1.0 + erf( (intensity-obs_mean)/( np.sqrt(2.0)*obs_std ))))
    return decision > observer