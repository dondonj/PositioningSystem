from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from server.model import *

from datetime import datetime, timedelta

class Database():
    """
    All methods that can be used on the database 
    """

    def __init__(self):
        """
        initialisation of the database 
        """
        print("initialisation")
        self.engine = create_engine('sqlite:///server/rssi.db', connect_args={'check_same_thread': False}, echo=False)
        base.metadata.create_all(self.engine)
        self.maker = sessionmaker(bind=self.engine)
        # self.session = scoped_session(self.maker())
        self.session = self.maker()
    
    def add_to_database(self, object):
        """
        Method that push object into the database
        """
        print("Enter adding part")       
        if self.session:
            try:
                self.session.add(object)
                self.session.commit()
                print("added")
            except:
                print("An error occured, this session is false or none")
                print(self.session)
                self.session.rollback()
                raise
    






    """ACCESS POINTS"""
    def get_ap(self, mac_address):
        """
        Method that return a specific access point given a mac_address
        """
        ap = self.session.query(AccessPoint).filter_by(mac_address=mac_address).first()
        if ap:
            return ap
        else:
            return False
    
    def get_ap_id(self, ap):
        """
        Method that return a specific access point given a mac_address
        """
        ap = self.session.query(AccessPoint).filter_by(mac_address=ap.mac_address).first()
        return ap.id
            
    
    def get_ap_all(self):
        """
        Method that return all access points
        """
        ap_query = self.session.query(AccessPoint).all()
        if ap_query:
            return ap_query
        else:
            return False
    





    """SAMPLES"""
    def get_sample(self, source_address):
        """
        Method that return a specific sample given the source_address
        """
        sample = self.session.query(Sample).filter_by(source_address=source_address).first()
        if sample:
            return sample
        else:
            return False
    
    def get_sample_all(self):
        """
        Method that return all samples
        """
        sample_query = self.session.query(Sample).all()
        if sample_query:
            return sample_query
        else:
            return False
    
    def get_matching_samples(self, mac_addr):
        """ Method that get all samples and fetch those which are 1 sec old """
        sampleMatchingList = []

        samples = self.get_sample_all()
        now = datetime.strptime(datetime.now().strftime("%H:%M:%S"), "%H:%M:%S")
        for sample in samples:
            if (sample.source_address == mac_addr) and (datetime.strptime(sample.timestamp, "%H:%M:%S") - now < timedelta(seconds=1)):
                sampleMatchingList.append(sample)

        return sampleMatchingList
    





    """FINGERPRINTS"""
    def get_fingerprint_all(self):
        """
        Method that return all samples
        """
        fingerprint_query = self.session.query(FingerprintValue).all()
        return fingerprint_query
    
    def get_fingerprint_id(self, fingerprint):
        """
        Method that return specific fingerprint id given fingerprint
        """
        fp = self.session.query(FingerprintValue).filter_by(loc_id=fingerprint.loc_id, ap_id=fingerprint.ap_id, rssi=fingerprint.rssi).first()
        return fp.id
    
    def exist_fingerprint(self, fingerprint):
        """
        Method that return True or False if the fingerprint exist
        """
        fp = self.session.query(FingerprintValue).filter_by(loc_id=fingerprint.loc_id, ap_id=fingerprint.ap_id, rssi=fingerprint.rssi).first()
        if fp:
            return True
        else:
            return False







    """LOCATIONS"""
    def get_location_all(self):
        """
        Method that return all location
        """
        location_query = self.session.query(Location).all()
        return location_query
    
    def get_loc(self, loc):
        """
        Method that return a specific sample given the source_address
        """
        location = self.session.query(Location).filter_by(id=loc.id).first()
        if location:
            return location
    
    def get_loc_id(self, loc):
        """
        Method that return a specific location id given location
        """
        loc = self.session.query(Location).filter_by(x=loc.x, y=loc.y, z=loc.z).first()
        return loc.id
    
    def exist_loc(self, loc):
        """
        Method that return True or False if the location exist
        """
        loca = self.session.query(Location).filter_by(x=loc.x, y=loc.y, z=loc.z).first()
        if loca:
            return True
        else:
            return False







    """CALIBRATING MOBILE"""
    def get_calibrating_all(self):
        """
        Method that return all calibration
        """
        calibrating_query = self.session.query(CalibratingMobile).all()
        return calibrating_query
    
    def del_calibrating_all(self, mac_addr):
        """
        Method that delete calibration mobile values
        """
        list_of_calibration = self.get_calibrating_all()
        for calib in list_of_calibration:
            if calib.mac_address == mac_addr:
                self.session.delete(calib)
        self.session.commit()
    
    def exist_calib(self, calib):
        """
        Method that return True or False if the calibrating mobile exist
        """
        calibration = self.session.query(CalibratingMobile).filter_by(mac_address=calib.mac_address, loc_id=calib.location).first()
        if calibration:
            return True
        else:
            return False
