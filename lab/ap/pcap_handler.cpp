#include "pcap_handler.h"
#include "http.h"
#include <radiotap_iter.h>
#include <string>

using namespace std;

string mac2string(unsigned char mac[6]) {
  char mac_c_str[18];
  sprintf(mac_c_str, "%02X:%02X:%02X:%02X:%02X:%02X\0", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  return string{mac_c_str};
}

/*
 * \function process_pkts PCAP callback function
 * \param user a pointer (to be cast) to a RSSILog variable
 * \param pkt a pointer to a rtap header
 * \param bytes a pointer to the captured packet, starting by the radiotap header
 */
void process_pkts(u_char* user, const struct pcap_pkthdr *pkt, const u_char *bytes) {
  /*
   * TODO: for each packet, extract the source address, the RSSI value(s),
   * the antenna index when present, and get system time. Each RSSI goes
   * to one element in the user->samples vector.
   * After dealing with the packet, check the first vector element
   * timestamp against current time. If it is older than 1 second, send
   * the samples (call send_samples from http.h)
   * */
  // TODO: your code here
  	int rssi;
	struct timeval timestamp_sys ;
	int timestamp;
	int antenna;

	auto rtap_hdr=(struct ieee80211_radiotap_header *) bytes;
	cout<<"test 1"<<endl;
	if(rtap_hdr->it_version==0){
		cout<<"test 2"<<endl;
		struct ieee80211_radiotap_iterator iter;
		int  err =  ieee80211_radiotap_iterator_init (&iter, rtap_hdr  , pkt->caplen  ,  nullptr ) ;
		if(!err){
			cout<<"test 3"<<endl;
			auto wifi_hdr = (struct ieee80211_header *) (bytes + iter._max_length);
			if(wifi_hdr->frame_control &0x00c0==0x0080){
				string source= mac2string(wifi_hdr->address2);
				cout << "\n\rsource :"<<source<<"\n\r";
				while(ieee80211_radiotap_iterator_next(&iter)==0){
					switch(iter.this_arg_index){
						case IEEE80211_RADIOTAP_DBM_ANTSIGNAL:{
							rssi= (int) *(iter.this_arg)-256;
							cout<<"RSSI: "+to_string(rssi)<<endl;
							break;
						}
						// case IEEE80211_RADIOTAP_CHANNEL:{
						// 	char channel=(int) *(iter.this_arg)-256;
						// 	break;
						// }
						case IEEE80211_RADIOTAP_ANTENNA:{
							antenna=(int) *(iter.this_arg)-256;
							cout<<"Antenna: "+to_string(antenna)<<endl;
							break;
						}
						case IEEE80211_RADIOTAP_TIMESTAMP:{
							timestamp=(int) *(iter.this_arg)-256;
							cout<<"Timestamp: "+to_string(timestamp)<<endl;
							break;
						}
						default:
						break;
					}
				}

				pcap_handler_user_data * user2=(pcap_handler_user_data *) user;
				RSSISample RSSI_sample={source,rssi,timestamp,antenna};
				RSSI_sample.ts = (struct timeval) pkt->ts;
				user2->samples.push_back(RSSI_sample);
				gettimeofday(&timestamp_sys, NULL);
				if(abs(timestamp_sys.tv_sec-user2->samples[0].ts.tv_sec) > 0){
					cout<<"sample sent \n\r"<<endl;
					send_samples(user2->samples,source);
				}
			}
		}
	}
}