# LO53 Lab Project

## Introduction

The goal of the project is to develop, deploy and test an indoor positioning system based on Wi-Fi. Unfortunately, this semester, no student will be allowed in the universities buildings, including UTBM, therefore you will be tasked with a subset of the original project.
An indoor positioning system based on Wi-Fi has to meet certain requirements to operate. These are:

- Choosing a family of algorithm. We will rely on algorithms developped during the exercises sessions.
- Choosing how to perform RSSI measurements. We use network probes that operate transparently inside the network.
    - Raspberry Pi 3 with USB Wi-Fi cards (that can switch to monitoring mode)
- Having a positioning server. We use one of the probes, or a virtual machine on a lab room computer
- Having mobile devices
- Choosing software development tools and language. We choose:
    - For the mobile devices: any HTTP-able device with a Wi-Fi interface card (smartphone, or laptop, for instance)
    - For the network probes: a C++ program using pcap to extract RSSI and MAC addresses from the captured Wi-Fi frames with a radiotap header
    - For the positioning server: a flask (Python) HTTP server, with a SQLite 3 database interfacing with flask through SQLAlchemy.

In each subsection describing what your objective is, fallback hardware and objectives will be defined so that you may succeed in producing working parts of the system.

## Prior tasks

### Forming your project team

You must choose 3 coworkers (so, your team will be 4 members strong). Try to have at least one that can provide a GNU/Linux laptop with a Wi-Fi card compatible with radiotap. Also try to mix your skills and have a panel of DB, C++, network, and Python skills when joining everyone's.

### Create a branch

Create a new branch in the git repository, named after your combined logins separated by '-'. A code structure is provided in this repository, in which you have to complete the source code where TODO comments are located.

### Forecast schedule

Due to the sanitary conditions, few sessions will take place on-site and the major part of the lab work will be carried out remotely. Thus, you'll have to prepare your work very carefully to make as good use as possible of the time allocated in the lab room. This also explains why there are _fallback hardware_ subsections in the instructions for you to be able to design, implement and test the required tasks.

## Network probes

### Compile the radiotap iter library

For the network probes, you need to compile the radiotap library. You have to get the radiotap.tar.gz file from git-info, then unpack it and compile it.

```bash
tar xzf radiotap.tar.gz
mkdir build
cd build/
cmake ../radiotap-library
make
```

When compilation is finished, you can copy the file libradiotap.so in /usr/lib (or /usr/lib64given your system architecture).

### Instructions

Our Raspberry Pi comes with a Raspbian system (GNU/Linux Debian distribution adapted to Raspberry Pi), that enables all of the regular linux interactions and softwares, including, but not limited to, C++ and libpcap library as well as the radiotap_iter headers.
The tasks are:

- implement the pcap handler in pcap_handler.cpp. This handler relies on ratiotap_iter to extract RSSI and MAC address values from the **incoming** frames. Then, both information are stored along the current timestamp. Last, you must clean the RSSI samples list from every sample older than 1 second. Note that, from the network probe point of view, the MAC addresses identifying a RSSI sample are the mobile devices MAC addresses.
- implement the send_samples function in http.cpp. This function builds an HTTP request whose parameters are ap with the current probe MAC address (from the server point of view, each probe must be identified), and as many parameters as there are mobile devices detected. Those parameters are named with the mobile device MAC address while their values are the average value of the RSSI samples available for the current address. For instance, probe with MAC@ 00:00:00:00:00:01 and RSSI samples (already averaged) ['01:00:00:00:00:00': -56.8, '02:00:00:00:00:00': -47.1] will send the following parameters: ap=00:00:00:00:00:01&01:00:00:00:00:00=-56.8&02:00:00:00:00:00=-47.1
- implement the options passing to the probe. It can receive 3 parameters:
    - -i with a parameter defines the RFMON interface to use (it is already in the code, use it as a model)
    - -h with a parameter defines the positioning server host (name or IP)
    - -p with a parameter defines the positioning server listening port

### Fallback hardware

Any laptop with a GNU/Linux distribution and a radiotap compatible Wi-Fi card will do. Instead of sending the RSSI information, you display the parameters string to your screen.

## Positioning server

The positioning server will be deployed on your computer, and tested with the **curl** command.

### Objectives and tasks

There are three main features to implement to the server:

- Handling RSSI sample packet from the probes
- Handling calibration start requests by a mobile device
- Handling calibration stop requests by a mobile device
- Handling positioning requests by a mobile device

To use the ORM mapping classes, fingerprint_value and calibrating_mobile, you must open the rssi.db file sqlite3 rssi.db and run the following SQL statements:

    CREATE TABLE fingerprint_value(id integer primary key, loc_id integer not null, ap_id integer not null, foreign key(ap_id) references accesspoint(id), foreign key(loc_id) references location(id));
    CREATE TABLE calibrating_mobile(mac_address text primary key, loc_id integer not null, foreign key(loc_id) references location(id));

#### Handling RSSI from probes

This task is handled by route `/rssi`, where a probe request will be processed as follows: it is composed of a parameter ap whose value is the sending probe MAC address, and of a series of pairs XX:XX:XX:XX:XX:XX=-YY.YYYY where:

- the X's are the measured devices MAC addresses hexadecimal characters
- and the Y's are the avg RSSI value digits for the corresponding MAC address over the last second

You have to put these information in the sqlite3 database named **rssi.db** whose schema can be displayed from the sqlite3 prompt through the command .schema.

#### Calibration start requests

This feature is routed to the path `/start_calibration`. A device must send its MAC address and its coordinates (x, y, z) to the server. Upon receiving these parameters, the positioning server moves samples from the sample table if they are less than 1 second old and their source address equals those of the device query. It also puts the location and the mobile device MAC address into table calibrating_mobile.

Then, the `/rssi` route also puts into fingerprint_value table all RSSI received for devices in calibrating_mobile table along with the AP MAC address who issued the RSSI and the corresponding location from the calibrating_mobile table.

You can test the calibration start request by using curl from a linux laptop or from a smartphone (then, use a browser instead of curl) with the following command:

    curl http://server_host:server_port/start_calibration?mac_addr=my_mac&x=my_x&y=my_y&z=my_z

where:

- my_mac is your mobile device Wi-Fi interface card MAC address (see ifconfig or ip addr commands)
- my_x, my_y and my_z are the coordinates of your location when running the curl command.

#### Calibration stop requests

This feature is routed to the path `/stop_calibration`. The server removes any entry whose mac_address matches the parameter mac_address from table calibrating_mobile.

You can test this feature with curl:

    curl http://server_host:server_port/stop_calibration?mac_addr=my_mac

#### Positioning requests

This feature is routed to the path `/locate`. It has one parameter, mac_addr, that identifies the mobile device. Upon receiving this request, the server gets all samples from sample table whose source address matches mac_addr and whose age is less than one second old. It uses these data to find the closest point in RSSI space from fingerprint_value table. This point must be returned to the device.

Again, test this feature with curl:

    curl http://server_host:server_port/locate?mac_addr=my_mac

## Mobile device

Since we have no access to the lab room, you will use curl as described above to test your code (it is even possible to really have the probe, i.e. your laptop, measure another device RSSI and communicate with the server through your local access point and network)

## Useful command line

Install dependencies:
    sudo apt-get install libpoco-dev
    sudo apt-get install aircrack-ng

Aircrack usage:
    -First of all, list out all available wireless cards connected to your PC using ‘iwconfig’ command.
    -Kill all the processes running on wireless card using 'sudo airmon-ng check kill'.
    -Start airmon-ng as a Monitor mode 'sudo airmon-ng start wlx00c0ca96f65a' (ID saw in the previous list).
    -Re-type 'iwconfig' to see the new name: wlan0mon.
    -Look at the nearby Wireless Access Points (optional): 'sudo airodump-ng wlan0mon'.

Launch the server using a terminal:
    -Go to PositioningSystem/lab
    -Type 'export FLASK_APP=server/server'
    -Type 'flask run --host=0.0.0.0'


Launch the probe script:
    -Go to the ap directory
    -Type 'sudo ./pcap'
