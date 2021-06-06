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
}
