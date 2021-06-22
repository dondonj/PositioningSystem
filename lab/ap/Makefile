CC=g++
CCFLAGS=-std=c++14 -I../resources/radiotap-library -I.
LDFLAGS=-lpcap -L../resources/build -lradiotap -lPocoNet
TARGET=pcap

all: $(TARGET)

$(TARGET): pcap.cpp defines.h http.o pcap_handler.o config.o
	$(CC) pcap.cpp -o pcap http.o pcap_handler.o config.o $(CCFLAGS) $(LDFLAGS)

%.o: %.cpp %.h
	$(CC) $(CCFLAGS) -c $< -o $@
