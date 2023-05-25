#include <ros/ros.h>
#include <rosneuro_msgs/NeuroFrame.h>
#include <std_msgs/String.h>
#include <math.h>
#include <vector>
#include <numeric>
#include <iostream>


ros::Publisher thresholding_pub;
ros::Subscriber sub;
long seq;

float average(std::vector<float> const& v){
    if(v.empty()){
        return 0;
    }

    auto const count = static_cast<float>(v.size());
    return std::accumulate(v.begin(), v.end(), 0.0) / v.size();
}


void thresholdingCallback(const rosneuro_msgs::NeuroFrame::ConstPtr& msg) {
	bool found=false;
	std::vector<float>::const_iterator first = msg->eeg.data.begin();
	std::vector<float>::const_iterator last = msg->eeg.data.begin() + 32;
	std::vector<float> v(first, last);
	
	//std::vector<float> v = msg->eeg.data; //32*16 in this case, must be generalized
	auto const mean = average(v);
	//std::cout<<"MEAN: " << mean << std::endl;
	for(int i=0; i<v.size();i++){
		if(v[i]-mean > 20) { //10 is a random value just to test
			found=true;
			break;
		}
	}
	std_msgs::String result;
	if(found){
		std::cout<< seq <<": Blinking detected!"<< std::endl;
		
		seq++;
		result.data="Blinking detected!";
		thresholding_pub.publish(result);
		ros::Duration(0.5).sleep();
	}
	
	
}

int main(int argc, char** argv) {

	ros::init(argc, argv, "blink_detector");
	
	ros::NodeHandle n;
	seq=1;
	
	thresholding_pub = n.advertise<std_msgs::String>("blink_detection", 1);
	sub = n.subscribe("/neurodata_filtered", 1, thresholdingCallback);
	
	ros::spin();			
	
	return 0;

}



