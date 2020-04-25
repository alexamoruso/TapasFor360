#!/usr/bin/env python
# -*- Mode: Python -*-
# -*- encoding: utf-8 -*-
# Copyright (c) Alex Amoruso  alex.amoruso@hotmail.it   

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE" in the source distribution for more information.
import os, sys
from utils_py.util import debug, format_bytes
from BaseViewController import BaseViewController
DEBUG = 1

class ConventionalViewController(BaseViewController):

    def __init__(self):
        super(ConventionalViewController, self).__init__()
        

    def __repr__(self):
        return '<ConventionalViewController-%d>' %id(self)

    #TODO verificare la gestione del numero delle view nel caso multiview
    
    def getView(self, cur_view, angles):
        alpha      = angles[0]
        new_view   = cur_view
        roi_center = self.feedback['yaw_angles'][cur_view]
        tmin       = roi_center - self.feedback['treshold_angle'] - self.feedback['delta']
        if tmin<0:
            tmin = 360 + tmin
        tmax = roi_center + self.feedback['treshold_angle'] + self.feedback['delta']
        if (cur_view != 0):
            if (alpha < tmin):
                new_view = cur_view - 1
            elif (alpha > tmax):
                new_view = cur_view + 1
                if new_view >= self.feedback['n_views']:
                    new_view = 0
        else:
            if (alpha > tmax and alpha < 180):
                new_view = 1
            elif (alpha < 280 and alpha > 180):
                new_view=self.feedback['n_views']-1
        return new_view

    
     