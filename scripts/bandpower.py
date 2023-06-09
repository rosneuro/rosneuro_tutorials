#!/usr/bin/env python
import rospy
import numpy as np
import copy
from rosneuro_msgs.msg import NeuroFrame
from std_msgs.msg import Float32MultiArray, MultiArrayDimension

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
	new_msg = Float32MultiArray()

	new_msg.layout.dim = [MultiArrayDimension()]
	
	new_msg.layout.dim[0].label = "height";
	new_msg.layout.dim[0].size   = old_message.eeg.info.nchannels;
	new_msg.layout.dim[0].stride = old_message.eeg.info.nchannels;
	new_msg.layout.data_offset = 0;

	# Pack the new data
	new_msg.data = data

	return new_msg


def main():
	global new_data, current_frame, seq
	new_data = False
	seq = 0
	np.seterr(divide = 'ignore') #just to avoid warnings when applying log10
	# Init the node
	rospy.init_node('bandpower')
	# Init the Publisher
	hz = rospy.get_param('rate', 16) # data.sr / nsample
	pub = rospy.Publisher('bandpower', Float32MultiArray, queue_size=1)
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
