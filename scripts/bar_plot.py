#!/usr/bin/env python
import rospy
import numpy as np
import copy
from rosneuro_msgs.msg import NeuroFrame
import tkinter  as tk 
from tkinter import *
from tkinter import ttk



seq= 0
#RANDOM VALUES, WILL BE INITIALIZED IN THE FIRST CALLBACK
nsamples = 0
nchannels = 0
buf = None
avgs = None
pg_val=None
ch=0

def callback(data):
	global pg_val
	pg_val.set(data.eeg.data[ch])
		
	

def main():
	global pg_val,var,my_w
	rospy.init_node('bar_plot', anonymous=True)
	rospy.Subscriber('bandpower', NeuroFrame, callback)
	my_w = tk.Tk()
	my_w.geometry("400x200")
	my_w.title('Bandpower of channel ' + str(ch))
	pg_val = DoubleVar()
	pg_val.set(0)
	s = ttk.Style()
	s.theme_use("classic")
	s.configure("Vertical.TProgressbar", background='green')
	prg1 = ttk.Progressbar(my_w,orient = HORIZONTAL, variable=pg_val,length = 100, maximum=2, mode ="determinate", style="Vertical.TProgressbar")
	label1 = Label( my_w, text='0')
	label1.place(relx=.01,rely=.3)
	label1 = Label( my_w, text='1')
	label1.place(relx=.97,rely=.3)
	#prg1.place(relx=.2,rely=.5)
	prg1.pack(fill=X, expand=1)
	# Keep the window open
	my_w.mainloop()
	while not rospy.is_shutdown():
		my_w.update()
		rospy.spin()

if __name__ == '__main__':
	main()
