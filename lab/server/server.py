from flask import Flask
from flask import request

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

import time

app = Flask(__name__)

engine = create_engine('sqlite:///rssi.db', echo=True)
base = declarative_base()
base.metadata.create_all(engine)

# app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rssi.db'
# db = SQLAlchemy(app)


Session = sessionmaker(bind=engine)
session = Session()

class AccessPoint(base):
    __tablename__ = "accesspoint"
    id = Column(Integer, primary_key=True)
    mac_address = Column(String)

class Location(base):
    __tablename__ = "location"
    id = Column(Integer, primary_key=True)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)

class Sample(base):
    __tablename__ = "sample"
    ap_id = Column(Integer, ForeignKey("accesspoint.id"))
    source_address = Column(String, nullable=False, primary_key=True)
    timestamp = Column(Float, nullable=False, primary_key=True)
    rssi = Column(Float, nullable=False)
    ap = relationship("AccessPoint", backref="sample")

    def values(self, src, t, _rssi, _ap):
        source_address = src
        timestamp = t
        rssi = _rssi
        ap = _ap

class FingerprintValue(base):
    __tablename__ = "fingerprint_value"
    id = Column(Integer, primary_key=True)
    loc_id = Column(Integer, ForeignKey("location.id"))
    ap_id = Column(Integer, ForeignKey("accesspoint.id"))
    rssi = Column(Float, nullable=False)
    location = relationship("Location", backref="fingerprint_value")
    ap = relationship("AccessPoint", backref="fingerprint_value")

class CalibratingMobile(base):
    __tablename__ = "calibrating_mobile"
    mac_address = Column(String, primary_key=True)
    loc_id = Column(Integer, ForeignKey("location.id"))
    location = relationship("Location", backref="calibrating_mobile")

@app.route("/rssi", methods=['GET', 'POST'])
def rssi():
    """
	ToDO: Implement this function
	It receives data from the access points on the path /rssi
	with a parameter ap whose value is the sending AP MAC address
	and a series of pairs XX:XX:XX:XX:XX:XX=-YY.YYYY
	where the X's are the measured devices MAC addresses
		  and the Y's are the avg RSSI values for the corresponding
		  MAC address over the last second
	You have to put these information in the sqlite3 database
	named rssi.db whose schema can be displayed from the sqlite3
	prompt through the command .schema
	SQL Alchemy ORM classes and initialization are available above
	"""

    if request.method == 'POST':
        ap = request.args.get('ap')
        source_adress = request.args.get('source_adress')
        rssi = request.args.get('rssi')
        print(ap + "\n")
        print(source_adress + "\n")
        print(rssi + "\n")

        ap_id = AccessPoint(mac_address=ap)
        rssi_avrg = Sample(ap_id=ap_id,source_address=source_adress , timestamp=time.time(),rssi=rssi )

        session.add(ap_id)
        session.add(rssi_avrg)

        session.commit()
        session.close()
        return "POST ok"
    else:
        print("coucou")
        for instance in session.query(Sample).order_by(Sample.rssi):
            print(instance.ap_id, instance.rssi)
        return "GET ok"



@app.route("/start_calibration", methods=['GET', 'POST'])
def start_calibration():
    """
        TODO: implement this function
        It receives 4 parameters: mac_addr (string), x (float), y (float), and z (float)
        then must trigger 3 tasks:
        (1) Add MAC address and location to table calibrating_mobile
        (2) Find all samples in table sample, and whose source address matches mac_addr
            and whose timestamp is less than 1 second in the past.
            With those samples, insert into table fingerprint_value all entries with
            ap_id matching the AP that forwared the RSSI sample, location the device location
            and RSSI the RSSI from table sample
        (3) In /rssi route: add instructions that process all incoming RSSI samples like
            step (2) when received.
    """
    if request.method == 'POST':
        data = request.data

    else:

        return "ok"


@app.route("/stop_calibration", methods=['GET', 'POST'])
def stop_calibration():
    """
        TODO: implement this function
        It receives one parameter: mac_addr (string)
        It must delete any calibrating_mobile entry whose mac_address equal parameter mac_addr
    """
    # Your code here
    return "ok"


@app.route("/locate", methods=['GET', 'POST'])
def locate():
    """
        TODO: implement this function
        It receives one parameter: mac_addr (string)
        Must locate the device based on samples less than 1 second old, whose source address equals mac_addr
        These samples are compared to the content of fingerprint_value table
        Use the closest in RSSI algorithm to find a fingerprint sample matching current sample and return its location
    """
    # Your code here
    return None

