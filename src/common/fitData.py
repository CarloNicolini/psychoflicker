# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 16:56:28 2013

@author: carlo
"""

#This analysis script takes one or more staircase datafiles as input
#from a GUI. It then plots the staircases on top of each other on
#the left and a combined psychometric function from the same data
#on the right

from psychopy import data
import pylab
from numpy import average,std

def fitData(stairs,percent):

    allIntensities, allResponses = [],[]
    for  s in stairs.staircases:
        allIntensities.append( s.intensities )
        allResponses.append( s.data )

    for s in stairs.staircases:
       print "Mean for condition ",s.condition['label'],"=",average(s.reversalIntensities),"std=",std(s.reversalIntensities)

    #plot each condition
    pylab.subplot(221)
    #for stairNumber, thisStair in enumerate(allIntensities):
    pylab.plot(allIntensities[0], 'o-', label=stairs.staircases[0].condition['label'] )
    pylab.xlabel('Trials')
    pylab.ylabel('Speed [cm/s]')
    pylab.legend()

    # Get combined data
    combinedInten, combinedResp, combinedN = data.functionFromStaircase(allIntensities, allResponses, 10)

    # Fit curve - in this case using a Weibull function
    fit = data.FitFunction('weibullTAFC',combinedInten, combinedResp, guess=None)
    #fit = data.FitCumNormal(combinedInten,combinedResp)
    intensitiesDomainInterp = pylab.arange(min(allIntensities[0]), max(allIntensities[0]), 0.01)
    smoothResponses = fit.eval(intensitiesDomainInterp)
    thresh = fit.inverse(percent)

    #Plot fitted curve
    pylab.subplot(222)
    pylab.axis(xmin=min(allIntensities[0]),xmax=max(allIntensities[0]))
    pylab.xlabel('Speed [cm/s]')
    pylab.ylabel('Probability')
    pylab.plot(intensitiesDomainInterp, smoothResponses, '-')
    pylab.plot([thresh, thresh],[0,percent],'--')
    pylab.plot([0, thresh],[percent,percent],'--')
    pylab.title('Threshold at ' + str(percent) + '= %0.3f' % (thresh) )
    # Plot points
    pylab.plot(combinedInten, combinedResp, 'o')
    pylab.ylim([0,1])

    # SECOND CONDITION, the plots are in a second row, under
    pylab.subplot(223)
    #for stairNumber, thisStair in enumerate(allIntensities):
    pylab.plot(allIntensities[1], 'o-', label=stairs.staircases[1].condition['label'] )
    pylab.xlabel('Trials')
    pylab.ylabel('Speed [cm/s]')
    pylab.legend()

    # Get combined data
    combinedInten, combinedResp, combinedN = data.functionFromStaircase(allIntensities[1], allResponses[1], 10)

    #fit curve - in this case using a Weibull function
    #fit = data.FitFunction('weibullTAFC',combinedInten, combinedResp, guess=None)
    fit = data.FitCumNormal(combinedInten,combinedResp)

    intensitiesDomainInterp = pylab.arange(min(allIntensities[1]), max(allIntensities[1]), 0.01)
    smoothResponses = fit.eval(intensitiesDomainInterp)

    thresh = fit.inverse(percent)
    #print "Threshold at " + str(percent) +"% with Cumulative Normal= ",thresh

    #Plot fitted curve
    pylab.subplot(224)
    pylab.axis(xmin=min(allIntensities[1]),xmax=max(allIntensities[1]))
    pylab.xlabel('Speed [cm/s]')
    pylab.ylabel('Probability')
    pylab.plot(intensitiesDomainInterp, smoothResponses, '-')
    pylab.plot([thresh, thresh],[0,percent],'--')
    pylab.plot([0, thresh],[percent,percent],'--')
    pylab.title('Threshold at ' + str(percent) + '= %0.3f' % (thresh) )
    # Plot points
    pylab.plot(combinedInten, combinedResp, 'o')
    pylab.ylim([0,1])

    pylab.show()