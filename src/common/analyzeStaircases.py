#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ####################################################################
#  2011-2014 Carlo Nicolini carlo.nicolini@iit.it
#  2011-2014 Sara Agosta sara.agosta@iit.it
#  2011-2014 Lorella Battelli  lbattell@bidmc.harvard.edu
#  This file is part of PsychoFlicker a battery of tests for visual psychophysics
#
#  PsychoFlicker is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the
#  Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# ####################################################################

from psychopy import data
import pylab
from numpy import average,std

def analyzeStaircases(stairs,nReversals):

    allIntensities,allResponses=[],[]
    nStairs=0
    for  s in stairs.staircases:
        allIntensities.append( s.intensities )
        allResponses.append( s.data )
        nStairs=nStairs+1

    lines, names = [],[]
    for stairIndex, thisStair in enumerate(allIntensities):
        pylab.subplot(1,nStairs,stairIndex)
        rev = stairs.staircases[stairIndex].reversalIntensities
        intens = stairs.staircases[stairIndex].intensities
        pylab.title('Threshold='+str(average(rev[(len(rev)-nReversals):len(rev)])))
        pylab.plot(intens, 'o-',label=stairs.staircases[stairIndex].condition['label'])
        pylab.xlabel('Trial')
        pylab.grid()
        pylab.ylabel('Speed [cm/s]')
        pylab.legend()

    pylab.show()