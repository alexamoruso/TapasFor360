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
import os, sys
from pprint import pformat
import time, datetime
import gobject
import gst
#
from twisted.internet import defer, reactor
from utils_py.util import debug, format_bytes
from BaseMediaEngine import BaseMediaEngine

DEBUG = 2

class GstMediaEngine(BaseMediaEngine):
    #qtdemux for video/mp4
    #mpegtsdemux for video/mpegts
    #matroskademux and for vp8_dec video/webm   


    #! capsfilter name=capsfilter
    #! %s

    PIPELINE = '''
appsrc name=src is-live=0 max-bytes=0
    ! identity sync=true single-segment=true
    '''

    VIDEO_NODEC = '''
    ! queue name=queue_v max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=%d
    ! %s
    '''

    VIDEO_DEC = ''' 
    ! %s name=parser
    ! queue name=queue_v max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=%d
    ! %s
    '''

    WITH_DEMUX      = '! %s name=demux demux.'
    
    ###PIPELINE = '''
###appsrc name=src is-live=0 max-bytes=0
    ###! identity sync=true single-segment=true
    ###! %s name=demux
    ###'''

    ###VIDEO_NODEC = ''' 
###demux.
    ###! queue name=queue_v max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=%d
    ###! %s
    ###'''

    ###VIDEO_DEC = ''' 
###demux.
    ###! %s name=parser
    ###! queue name=queue_v max-size-buffers=0 max-size-time=0 max-size-bytes=0 min-threshold-time=%d
    ###! %s
    ###'''
    

    DEMUX_MPEGTS    = 'mpegtsdemux'
    DEMUX_MP4       = 'qtdemux' 
    DEMUX_WEBM      = 'matroskademux' 

    PARSE_H264      = 'h264parse'
    PARSE_MATROSKA  = 'matroskaparse'

    DEC_VIDEO_H264  = '''ffdec_h264 ! timeoverlay ! videorate ! videoscale ! video/x-raw-yuv,width=1280,height=720,framerate=30/1 ! xvimagesink qos=0'''
    DEC_VIDEO_VP8   = '''vp8dec ! timeoverlay ! videorate ! videoscale ! ! video/x-raw-yuv,width=1280,height=720,framerate=30/1 ! xvimagesink'''

    #DEC_VIDEO_H264 = '''avdec_h264 direct-rendering=0 ! timeoverlay ! videorate ! videoscale ! xvimagesink'''
    #DEC_VIDEO_VP8 = '''vp8dec ! timeoverlay ! videorate ! videoscale ! xvimagesink'''

    def __init__(self, decode_video=True, min_queue_time=10):
        BaseMediaEngine.__init__(self, min_queue_time)
        self.decode_video = decode_video
        self.pipeline = None
        #self.ind = 0

    def __repr__(self):
        if self.decode_video:
            return '<GstMediaEngine-%d>' %id(self)
        else:
            return '<GstNoDecMediaEngine-%d>' %id(self)

    def start(self):
        try:
            BaseMediaEngine.start(self)
            
            #
            q = 0 #int(self.min_queue_time*1e9)   #min-threshold-time
            v_sink = 'fakesink sync=true'
            if self.getVideoContainer()   == 'MP4':
                demux = self.DEMUX_MP4
                parse = self.PARSE_H264
            elif self.getVideoContainer() == 'MPEGTS':
                demux = self.DEMUX_MPEGTS
                parse = self.PARSE_H264
            elif self.getVideoContainer() == 'WEBM':
                demux = self.DEMUX_WEBM
                parse = self.PARSE_WEBM
            else:
                debug(0, '%s Cannot play: video/%s', self, self.getVideoContainer())
                #return
                sys.exit(1)
                
            debug(DEBUG, '%s Playing type: video/%s', self, self.getVideoContainer())
            if self.decode_video:
                if not self.getVideoContainer() == 'WEBM':
                    v_sink = self.DEC_VIDEO_H264
                else:
                    v_sink = self.DEC_VIDEO_VP8
                desc = self.PIPELINE %(demux) + self.VIDEO_DEC %(parse, q, v_sink)
            else:
                if self.getVideoContainer()   == 'MP4':
                    desc = self.PIPELINE + self.VIDEO_NODEC %(q, v_sink)
                elif self.getVideoContainer() == 'MPEGTS':
                    desc = self.PIPELINE + self.WITH_DEMUX %(demux) + self.VIDEO_NODEC %(q, v_sink)
                
            debug(DEBUG, '%s pipeline: %s', self, desc)
            print "PIPELINE: " + desc
            self.pipeline   = gst.parse_launch(desc)
            self.queue      = self.pipeline.get_by_name('queue_v')
            self.status     = self.PAUSED
            self.pipeline.set_state(gst.STATE_PAUSED)
            self.onRunning()
        except Exception, e:
            print(">>>>>>>>>>>> EXCEPTION: " + str(e))
            sys.exit(1)

    def onRunning(self):
        print ">>>>>>>>>>>>>>>>>>>>>>>>>> QUEUE TIME: " + str(self.getQueuedTime())
        print ">>>>>>>>>>>>>>>>>>>>>>>>>> STATUS PLAYER: " + str(self.status)
        
        if self.getQueuedTime() >= self.min_queue_time and self.status == self.PAUSED:
            self.pipeline.set_state(gst.STATE_PLAYING)
            self.status = self.PLAYING
            self.emit('status-changed')
        elif self.getQueuedTime() == 0 and self.status == self.PLAYING:
            self.pipeline.set_state(gst.STATE_PAUSED)
            self.status = self.PAUSED
            self.emit('status-changed')
        reactor.callLater(0.1, self.onRunning)

    def stop(self):
        BaseMediaEngine.stop(self)
        #
        if self.pipeline:
            self.pipeline.set_state(gst.STATE_PAUSED)
            self.pipeline = None

    def pushData(self, data, fragment_duration, level, caps_data):
        try:
            #f= open("{}.mp4".format(self.ind),"w+")
            #f.write(data)
            #self.ind += 1
            #f.close()
            
            
            buf             = gst.Buffer(data)
            buf.duration    = long(fragment_duration * 1e9)
            #print(">>>>>>>>>>>>> Push data", level, fragment_duration, len(data), len(buf))
            debug(DEBUG, '%s pushData: pushed %s of data (duration= %ds) for level %s', self, 
                format_bytes(len(data)),
                fragment_duration,
                level)
            
            self.pipeline.get_by_name('src').emit('push-buffer', buf)
            del buf
        except Exception, e:
            print(">>>>>>>>>>>> EXCEPTION: " + str(e))
            sys.exit(1)#HARD, better to do return

    def _on_video_buffer(self, pad, buf):
        if isinstance(buf, gst.Buffer):
            buf.set_caps(self.video_caps)
        return True

    def getQueuedBytes(self):
        #print ("CURRENT LEVEL BYTES",self.queue.get_property('current-level-bytes'))
        return self.queue.get_property('current-level-bytes')


    def getQueuedTime(self):
        #print ("CURRENT LEVEL TIME", self.queue.get_property('current-level-time'))
        return self.queue.get_property('current-level-time')*1e-9
