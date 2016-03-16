#!/usr/bin/env python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time

def is_gpio_in(id):
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(id,GPIO.IN,pull_up_down = GPIO.PUD_DOWN)
	GPIO.add_event_detect(id,GPIO.RISING)
	GPIO.add_event_callback(id,rising_callback,100)
	while True:
		print "working"
def ris_callback(channel):
	return 	True
if __name__ == "__main__":
	is_gpio_in(11)

