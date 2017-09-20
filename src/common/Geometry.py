# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 10:27:11 2013

@author: carlo
"""

import numpy as np


def cartesian2polar(x):
    angle = np.arctan2(x[1], x[0])
    magnitude = np.sqrt(np.dot(x, x))
    return np.array([magnitude, angle])


def polar2cartesian(v):
    x = v[0] * np.cos(v[1])
    y = v[0] * np.sin(v[1])
    return np.array([x, y])


def normalized(x):
    return x / np.linalg.norm(x)


def rectangleCenter(rect):
    halfX = (rect[0] + rect[2]) / 2
    halfY = (rect[1] + rect[3]) / 2
    return np.array([halfX, halfY])
