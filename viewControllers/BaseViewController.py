#!/usr/bin/env python
# -*- Mode: Python -*-
# -*- encoding: utf-8 -*-
# Copyright (c) Vito Caldaralo <vito.caldaralo@gmail.com>

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE" in the source distribution for more information.
import os, sys, inspect
from utils_py.util import debug


'''feedback = dict('queued_bytes':[B],
   'queued_time':[s],
   'max_buffer_time':[s],
   'bwe':[B/s],
   'level':[],
   'max_level':[],
   'cur_rate':[B/s],
   'max_rate':[B/s],
   'min_rate':[B/s],
   'player_status':[boolean],
   'paused_time':[s],
   'last_fragment_size':[B],
   'last_download_time':[s],
   'downloaded_bytes':[B],
   'fragment_duration':[s],
   'rates':[B/s{list}],
   'is_check_buffering:[boolean]
)'''

class BaseViewController(object):
#devo popolare dei field dal player in cui mantengo le informazioni relative alle view
    def __init__(self):
        self.idle_duration = 4
        self.control_action =  None
        self.feedback = None           

    def __repr__(self):
        return '<BaseViewController-%d>' %id(self)

    def getAngles(self):
        return self.feedback['view_angles']
        
    def getView(self):
        #raise NotImplementedError("Subclasses should implement "+inspect.stack()[0][3]+"()")
        return 0
   
    
    def setPlayerFeedback(self, dict_params):
        '''
        Sets the dictionary of all player feedback used for the control. 
        This method is called from ``TapasPlayer`` before ``calcControlAction``

        :param dict_params: dictionary of player feedbacks.
        '''
        self.feedback = dict_params



