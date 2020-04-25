#!/usr/bin/env python
# -*- Mode: Python -*-
# -*- encoding: utf-8 -*-
# Copyright (c) Giuseppe Cofano <g.cofano87@gmail.com>

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.
# See "LICENSE" in the source distribution for more information.
import os, sys
from numpy import array
import time
from utils_py.util import debug, format_bytes, CircularBuffer
from BaseController import BaseController

DEBUG = 1


class ElasticController(BaseController):

    def __init__(self, k1, k2, qL, qH):
        super(ElasticController, self).__init__()
        self.queue_low = qL
        self.queue_high = qH
        self.k1 = k1
        self.k2 = k2
        self.t_last = -1
        # flag to reset integral error when entering q > q_H or q < q_L
        self.int_error = 0
        self.prec_state = 0
        self.last_level = 0
        self.bwe_filt = -1
        self.horizon = 5
        self.bwe_vec = CircularBuffer(self.horizon)

    def __repr__(self):
        return '<ElasticController-%d>' % id(self)

    def calcControlAction(self):
        self.bwe_vec.add(self.feedback['bwe'])

        def __harmonic_mean(v):
            '''Computes the harmonic mean of vector v'''
            x = array(v)
            debug(DEBUG+2, "%s __harmonic_mean: Bwe vect: %s", self, str(x))
            m = 1.0/(sum(1.0/(x+1))/len(x))
            debug(DEBUG, "%s__harmonic_mean: Harmonic mean: %s/s", self, format_bytes(m))
            return m
        self.bwe_filt = __harmonic_mean(self.bwe_vec.getBuffer())
        e = self.__getError()

        # this "if" sets the flag zero_int_err to nullify the integral
        # error when entering q > q_H or q < q_L
        if e == 0: 
            self.prec_state = 1
            zero_int_error = 1
        elif e > 0 and self.prec_state == 0: 
            self.prec_state = 2
            zero_int_error = 1
        elif e < 0 and self.prec_state == 2:
            self.prec_state = 0
            zero_int_error = 1
        else: 
            zero_int_error = 0

        max_rate = self.feedback['max_rate']
        min_rate = self.feedback['min_rate']
        d = self.feedback['player_status']
        if self.t_last < 0:
            delta_t = 0
            self.int_error = e
        else:
            delta_t = time.time() - self.t_last
            if zero_int_error == 1:  #flag to nullify the integral error when entering q > q_H or q < q_L
                #DEBUG && log('Force integral error == 0');
                self.int_error = 0
            self.int_error += delta_t * e

        self.t_last = time.time()
        q = self.feedback['queued_time']
        if q < self.__getQueueLowWM() or q > self.__getQueueHighWM() or self.feedback['is_check_buffering']:
            '''The control law is b / ( 1 - k1 e - k2 ei)'''
            den = 1 - self.k1*e - self.k2*self.int_error
            bwe = self.bwe_filt
            u = bwe/den
            if den <= 0 or u >= max_rate:
                # Make sure that the maximum rate can be selected
                u = max_rate + 2000
                debug(DEBUG, '%s calcControlAction: Max rate reached. Anti windup active', self)
                self.__resetIntegralError(delta_t * e)
            elif u <= min_rate:
                u = min_rate
                self.__resetIntegralError(delta_t * e)
                debug(DEBUG, '%s calcControlAction: Min rate reached. Anti windup active', self)
        else:
            u = self.feedback['cur_rate']

        level_u = self.quantizeRate(u)
        if q > self.__getQueueHighWM() and level_u < self.last_level:
            level_u = self.last_level
            debug(DEBUG, '%s Prevented switch down when q > q_H',self)
        self.last_level = level_u
        debug(DEBUG, '%s calcControlAction: u: %s/s q: %.2f e: %.2f int_err: %.2f delta_t: %.2f level_u: %d',  self, 
            format_bytes(u), q, e, self.int_error, delta_t, level_u)
        return u

    def onPaused(self):
        self.int_error = self.__getError()
        debug(DEBUG, '%s Paused. Resetting integral error', self)

    def __resetIntegralError(self, data):
        debug(DEBUG, '%s Resetting integral error', self)
        self.int_error -= data

    def __getQueueLowWM(self):
        return self.queue_low

    def __getQueueHighWM(self):
        return self.queue_high

    def __getError(self):
        q = self.feedback['queued_time']
        if q > self.__getQueueHighWM():
            return q - self.__getQueueHighWM()
        elif q < self.__getQueueLowWM():
            return q - self.__getQueueLowWM()
        return 0
