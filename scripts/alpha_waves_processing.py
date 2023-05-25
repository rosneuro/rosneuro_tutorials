#!/usr/bin/env python
import rospy
import numpy as np
import copy
from rosneuro_msgs.msg import NeuroFrame

def callback(data: NeuroFrame):
	global new_data, current_frame
	# Save the new data
	current_frame = data
	new_data = True

def buffered_bandpower(data: NeuroFrame):
	global buffer, seq, avgs
	
	# INITIALIZATION
	if(seq==0):
		# Create a zero filled matrix
		buffer  = np.zeros((data.eeg.info.nchannels, data.sr))
		# Create a zero filled array
		avgs = np.zeros((data.eeg.info.nchannels,))
		
	# UPDATE BUFFER
	# New data 
	eeg_data = np.array(data.eeg.data).reshape((data.eeg.info.nchannels, data.eeg.info.nsamples)) #all channels
	# Remove the old data from the buffer
	buffer = np.delete(buffer,[index for index in range(data.eeg.info.nsamples)], axis=1)
	# Add the new data to the buffer
	buffer = np.hstack((buffer, eeg_data))

	# Update the sequence number
	seq = seq + 1

	# If the buffer is filled
	if(seq * data.eeg.info.nsamples >= data.sr):
		# Processing:
		for index in range(data.eeg.info.nchannels):
			# Compute the bandpower
			current_row = np.multiply(buffer[index], buffer[index])
			current_row = np.log10(current_row)
			avgs[index] = np.average(current_row)
	
	return tuple(avgs)


def generate_new_message(data, rate, old_message):
	# Starting from the old message generate the new one
	global seq
	
	new_msg = copy.deepcopy(old_message)
	now = rospy.get_rostime()
	new_msg.sr = rate 
	new_msg.header.seq = seq - 1 
	new_msg.header.stamp.secs = now.secs
	new_msg.header.stamp.nsecs = now.nsecs
	new_msg.eeg.info.nsamples = 1

	# Pack the new data
	new_msg.eeg.data = data

	return new_msg


def main():
	global new_data, current_frame, seq
	new_data = False
	seq = 0

	# Init the node
	rospy.init_node('alpha_waves_processing')
	# Init the Publisher
	hz = rospy.get_param('rate', 16) # data.sr / nsample
	pub = rospy.Publisher('bandpower', NeuroFrame, queue_size=1)
	# Setup the Subscriber
	rospy.Subscriber('neurodata_filtered', NeuroFrame, callback)
	rate = rospy.Rate(hz)

	while not rospy.is_shutdown():
		# Wait until new data arrives
		if new_data:
			new_data = buffered_bandpower(current_frame)
			new_msg = generate_new_message(new_data, hz, current_frame)
			pub.publish(new_msg)
			new_data = False
		rate.sleep()
		
if __name__ == '__main__':
  main()
