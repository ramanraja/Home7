# Maps users to their devices

# pip install dataset

from collections import OrderedDict
import pymysql
from random import randint
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset
import json
from .testids import test_ids
from config import Config

class DeviceMap():
    def __init__(self, database):
        self.db = database
        self.table_name = 'devices'   # it is case sensitive *
        self.table = None 
        
    def setup (self): # You MUST call this function immediately after creating this object
        tabs = self.db.tables  # this is to check: was the table already present before we came here?
        #print ('Existing tables: ', tabs)
        # if the table is present, open it, otherwise create a new table:
        self.table = self.db[self.table_name]  # <- this creates the table, anyway
        if (not self.table_name in tabs):   
            print (self.table_name, ' table not found!') #  (but it would have been created by now)
            return False  # this tells the caller: we have created a blank table just now, so add some test data
        print (self.table_name, ' table found.') # The table was already present,...
        return True                              # ...so, do not add any test data!
    
    
    # get a database record set for a given user id. Return value is a RecordSet object
    # The table has one-to-many mapping: for each intof_id there are a number of device_ids
    def get_user_records (self, intof_id):
        recordset = self.table.find (intofid=intof_id) # returns None if no recrod is found
        #print (recordset)
        if recordset is None:
            return None
        else:
            print (type(recordset))
        return recordset           
        
    # get only the device ids for a given user  
    # The table has one-to-many mapping: for each intofid there are a number of devices
    def get_user_devices (self, intof_id):
        recordset = self.table.find (intofid=intof_id) # returns None if no recrod is found
        #print (recordset)
        if recordset is None:
            return None
        #print (type(recordset))
        retval = []
        for rec in recordset:
            dev = rec['deviceid']  
            retval.append (dev)
        return (retval)  # this can be an empty list also
        
    # To avoid inserting duplicate records, check if it alreay exists
    def device_exists (self, intof_id, device_id):
        recordset = self.table.find_one (intofid=intof_id, deviceid=device_id) # returns None if no recrod is found
        # * NOTE:  table.find() will return an empty RecordSet object, so it will never be 'None'. So use table.find_one() *
        #print (recordset)
        if recordset is None:
            return False
        return True
        
    def add_device (self, device):
        print ('Adding device: ', device)
        intof_id = device.get('intof_id')
        if  intof_id is None or len (intof_id)==0:
            err = 'User ID is missing'
            return ({'success' : False, 'msg' :  err})
        device_id = device.get('device_id')
        if  device_id is None or len (device_id)==0:
            err = 'Device ID is missing'        
            return ({'success' : False, 'msg' :  err}) 
        print ('New device: ', end='')
        device_record = {'intofid' : intof_id, 'deviceid' : device_id}
        print (device_record)
        try:
            self.table.insert (device_record)  
        except Exception as e:
            return ({'success' : False, 'msg' :  str(e)})
        return ({'success' : True, 'msg' :  'Device added.'})            
            
     
    # ---------------- utility helpers ------------------------------------------
        
    def add_test_data (self):
        dev1 = { 'intof_id' : test_ids[0], 'device_id' : 'TOF-ABC123' }
        dev2 = { 'intof_id' : test_ids[0], 'device_id' : 'TOF-DEF321' }        
        dev3 = { 'intof_id' : test_ids[1], 'device_id' : 'TOF-CBA135' }
        dev4 = { 'intof_id' : test_ids[1], 'device_id' : 'TOF-FED246' }
        self.add_device (dev1)
        self.add_device (dev2)
        self.add_device (dev3)
        self.add_device (dev4)
        print ('4 test devices added.')
    
    
    def print_all_data (self):
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  ({}) {} -> {}'.format(row['id'], row['intofid'],row['deviceid'])) 
        print ('Total rows: ', len(self.table))
        #print ('-'*25)
    

    def print_filtered_data (self, data):
        count = 0
        #print (type(data))  # this may be a result iterator (possibly, of length 0,1 or more)
        if isinstance (data, dataset.util.ResultIter):
            for d in data:
                print (d)
                count += 1
        elif isinstance (data, OrderedDict): # A single record was returned
            print (data)
            count = 1
        print ('Filtered rows: ', count)
        #print ('-'*25)
        return count   # NOTE: Now we have reached the end of the iterator, so it cannot be used again *
        

    def print_stats (self):
        # Get all table names
        print ('Tables in the db:')
        print (self.db.tables)
        print ('Your table is: ', self.table)
        # Number of rows in our table of interest
        print ('Rows in your table: ', len(self.table))
        # Get columns
        print ('Columns in your table:')
        print(self.table.columns)
        #print ('-'*25)            
              
#-----------------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------------

if (__name__ == '__main__'): 
    print ('initializing database..') 
    
    # format of database url is "dialect://user:password@host:port/dbname" 
    database_url = Config.DATABASE_URL           # take it directly from config.py file, not app.config
    
    print ('Using database: ', database_url)
    if database_url:
        db = dataset.connect (database_url) 
    else:
        db = dataset.connect()  # setup an environment variable named DATABASE_URL (defaults to :memory:)
    print ('Existing tables: ', db.tables)

    device_map = DeviceMap (db)
    
    # You must always call setup(). This is where the table is created
    table_exists = device_map.setup() 
    
    if (not table_exists):
        print ('Device mapping table was not found. Creating test entries anyway..')
        device_map.add_test_data()
    print()
        
    dev = { 'intof_id' : test_ids[2], 'device_id' : 'TOF-DDE876'}
    if device_map.device_exists (dev['intof_id'], dev['device_id']):
        print (f"Device {dev['intof_id']}/{dev['device_id']} already exists.")
    else:
        device_map.add_device (dev)
    print()
    device_map.print_stats()
    print()
        
    device_map.print_all_data()
    print()
        
    # Filter   
    iid = test_ids[0]
    print ('Searching for Intof id: ',iid)
    devs = device_map.get_user_records (iid)
    print ('Users records:')
    device_map.print_filtered_data (devs)  # RecordSet
    print()
        
    iid = test_ids[0]
    print ('Searching for Intof id: ',iid)
    devs = device_map.get_user_devices (iid)
    print ('Users devices:') # List
    print (devs)
    print()
            
    print ('Searching for non-existent user:')
    devs = device_map.get_user_devices ('None-Such')
    print ('Users devices:')
    device_map.print_filtered_data (devs)
    print()
                