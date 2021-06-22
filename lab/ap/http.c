#include "http.h"
#include <Poco/Net/Net.h>
#include <Poco/Net/HTTPClientSession.h>
#include <Poco/Net/HTTPRequest.h>
#include <Poco/Net/HTMLForm.h>
#include <map>
#include <set>
#include <cmath>
#include "config.h"

using namespace std;
using namespace Poco::Net;

void send_samples(RSSILog samples, string ap_mac_addr) {
  /*
   * TODO: Implement this function
   * It takes two parameters:
   * 	- samples with RSSI samples ordered by reception time
   * 	- ap_mac_addr the Raspberry Pi MAC address
   * 
   * It must send its MAC address as variable name ap
   * and a list of pairs DeviceMAC=RSSI where each DeviceMAC is unique
   * and RSSI are average RSSI values when multiple values exist for a
   * given DeviceMAC
   * 
   * The packet must be sent to http://localhost:8080/rssi
   * 
   * HTTP requests handling use Poco::Net API
   * */
  // TODO: your code here
    Configuration* conf = Configuration::getInstance();
    string serv_host = conf->getServerHost();
    unsigned short serv_port = conf->getServerPort();
    
    string URL = "http://"+serv_host+":"+to_string(serv_port)+"/rssi?ap=" + ap_mac_addr; 
    
    for (auto &sample : samples){   
      URL += "&" + sample.mac_address + "=" + to_string(sample.rssi);
    }
    
    HTTPClientSession HTTP_session(serv_host,serv_port);
    HTTPRequest HTTP_request(HTTPRequest::HTTP_POST,URL,HTTPMessage::HTTP_1_1);
    HTTP_session.sendRequest(HTTP_request);
}