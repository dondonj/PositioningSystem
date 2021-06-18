from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from server.model import *

class Database():
    """
    All methods that can be used on the database 
    """

    def __init__(self):
        """
        initialisation of the database 
        """
        self.engine = create_engine('sqlite:///server/rssi.db', echo=True)
        base.metadata.create_all(self.engine)
        self.maker = sessionmaker(bind=self.engine)
        self.session = self.maker()
    
    def add_to_database(self, object):
        """
        Method that push object into the database
        """
        self.session.add(object)
        self.session.commit()
    
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
        if ap:
            return ap.id
        else:
            return False
    
    def get_ap_all(self):
        """
        Method that return all access points
        """
        ap_query = self.session.query(AccessPoint).all()
        if ap_query:
            return ap_query
        else:
            return False
    
    def get_sample(self, source_address):
        """
        Method that return a specific sample given the source_address
        """
        sample = self.session.query(Sample).filter_by(source_address=source_address)
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
    
    def get_fingerprint_all(self):
        """
        Method that return all samples
        """
        fingerprint_query = self.session.query(FingerprintValue).all()
        if fingerprint_query:
            return fingerprint_query
        else:
            return False

    def get_location_all(self):
        """
        Method that return all location
        """
        location_query = self.session.query(Location).all()
        if location_query:
            return location_query
        else:
            return False
    
    def get_calibrating_all(self):
        """
        Method that return all calibration
        """
        calibrating_query = self.session.query(CalibratingMobile).all()
        if calibrating_query:
            return calibrating_query
        else:
            return False
