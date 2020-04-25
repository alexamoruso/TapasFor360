#!/bin/sh

#DEBUG=2 python play.py --url=http://devimages.apple.com/iphone/samples/bipbop/bipbopall.m3u8
DEBUG=2 GST_DEBUG=0 python play.py --url=${1} --csv=csvExample.csv -m nodec -a max
