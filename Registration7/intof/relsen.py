# relsen.py
# Backend code to add 'devices' or 'relsens' to the Intof database
# Keep this in sync with the RelsenMap class on Registration application; they are the same code.
# NOTE: Each individual relay or sensor is called a 'device' in the user parlance, but it is internally called a 'Relsen'.
# NOTE: This class serves only discovery; you need another full 'Device' class
 
# pip install dataset

# TODO: API for insert, update, delete
# TODO: factor out the common code to a base class (feature:instead of iterator, bulk downloads as a list)

##from urllib.request import urlopen
from collections import OrderedDict
import pymysql
from random import randint
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset
import json
from intof.testids import test_ids
from config import Config
#---------------------------------------------------------------------------------------------------------------

class RelsenMap ():

    def __init__ (self, database):
        self.db = database
        self.table_name = 'relsen'   # it is case sensitive *
        self.table = None 
             
             
    def setup (self): # You MUST call this function immediately after creating this object
        tabs = self.db.tables
        #print ('Existing tables: ', tabs)
        # if the table is present, open it, otherwise create a new table:
        self.table = self.db[self.table_name] 
        if (not self.table_name in tabs):   
            print (self.table_name, ' table not found!')
            return False
        print (self.table_name, ' table found.')
        return True
    
    
    # get a database record set for a given user id
    # The table has one-to-many mapping: for each intofid there are a number of relsens
    def get_user_records (self, intof_id):
        recordset = self.table.find (intofid=intof_id) # returns None if no recrod is found
        #print (recordset)
        if recordset is None:
            return None
        else:
            print (type(recordset))
        return recordset   
        
        
    # get only the endpoint and friendly name for a given user id
    # The table has one-to-many mapping: for each intofid there are a number of relsens
    def get_user_relsens (self, intof_id):
        recordset = self.table.find (intofid=intof_id) # returns None if no recrod is found
        #print (recordset)
        if recordset is None:
            return None
        #print (type(recordset))
        retval = []
        for rec in recordset:
            relsen = tuple ((rec['endpoint'], rec['fname']))  # A tuple is ordered and unmutable
            retval.append (relsen)
        return (retval)  # this can be an empty list also        
                
                
    def does_relsen_exist (self, intof_id, relsen_id):  # relsen_id: POWER1, POWER2 etc
        end_point = f'{intof_id}.{relsen_id}'
        existing =  self.table.find_one (intofid=intof_id, endpoint=end_point) 
        if (existing is None):
            return False
        return True
    
    
    def create_relsen (self, intof_id, end_point, friendly_name):  
        print ('Adding new relsen: ', end='')
        if  friendly_name is None or len (friendly_name)==0:
            err = 'Alexa name is missing'
            return ({'success' : False, 'msg' :  err})        
        relsen_record = {'intofid' : intof_id, 'endpoint' : end_point, 'fname' : friendly_name}
        print (relsen_record)
        try:
            self.table.insert (relsen_record)  
        except Exception as e:
            print ('EXCEPTION1: ', str(e))
            return ({'success' : False, 'msg' :  str(e)})
        return ({'success' : True, 'msg' :  'Relsen added.'})
              
        
    def upsert_relsen (self, intof_id, end_point, friendly_name):  
        print ('Adding/updating relsen: ', end='')
        if  friendly_name is None or len (friendly_name)==0:
            err = 'Alexa name is missing'
            return ({'success' : False, 'msg' :  err})        
        relsen_record = {'intofid' : intof_id, 'endpoint' : end_point, 'fname' : friendly_name}
        print (relsen_record)
        try:
            self.table.upsert (relsen_record, keys=['intofid', 'endpoint'])  
        except Exception as e:
            print ('EXCEPTION2: ', str(e))
            return ({'success' : False, 'msg' :  str(e)})
        return ({'success' : True, 'msg' :  'Relsen added.'})

        
    # insert/update a device (ESP8266 can support upto 8 relays plus a sensor)
    def upsert_device (self, device):
        print ('Adding device: ', device)
        # Only logged in users can add a device, so their intof_id already exists in our system 
        intof_id = device.get('intof_id')
        if  intof_id is None or len (intof_id)==0:
            err = 'User ID is missing'
            return ({'success' : False, 'msg' :  err})
        device_id = device.get('device_id')
        if  device_id is None or len (device_id)==0:
            err = 'Device ID is missing'
            return ({'success' : False, 'msg' :  err}) 
        try:    
            # if the relsen is already there, update only the Alexa name    
            for key in device['relsens']:  # NOTE: The keys must be POWER1, POWER2 etc for Tasmota to understand
                relsen_id = key
                end_point = f'{device_id}.{relsen_id}'
                alexa_name = device['relsens'][key]
                result = self.upsert_relsen (intof_id, end_point, alexa_name)
                if result['success']==False :
                    return result  # abort, even if one relay fails to update
            return result  # return the last relay's result      
        except Exception as e:
            print ('EXCEPTION3: ', str(e))
            return ({'success' : False, 'msg' :  str(e)})
        return ({'success' : True, 'msg' :  'Device added/ updated.'})
        
        
    # ---------------- utility helpers ------------------------------------------
        
    def add_test_data (self):
        dev1 = {
            'intof_id' : test_ids[0], 'device_id' : 'TOF-ABC123', 'relsens' : 
            {'relay1' : 'tube light', 'relay2' : 'fan', 'relay3' : 'kitchen light', 'relay4' : 'AC' }
        }
        dev2 = {
            'intof_id' : test_ids[1], 'device_id' : 'TOF-DEF321', 'relsens' : 
            {'relay1' : 'portico lamp', 'relay2' : 'bedroom', 'relay3' : 'coffe maker', 'relay4' : 'desk lamp' }
        }
        self.upsert_device (dev1)
        self.upsert_device (dev2)
        print ('2 test devices added.')
    
    
    def print_all_data (self):
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  ({}) {} -> {} [{}]'.format(row['id'], row['intofid'],row['endpoint'],row['fname'])) 
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
        
        
    # TODO: This is only test code; use it to implement the actual update functionality for the class
    def test_update(self):    
        # use 'intofid' and 'endpoint' as a compound search key and update that single row 
        self.table.update (dict(intofid=test_ids[0], endpoint='TOF-ABC123.POWER2', fname='heater'), ['intofid', 'endpoint'])
        print ('Device updated.\n')
        
        # Update the endpoint itself, even though it is part of the search key:
        data = self.table.find_one (intofid=test_ids[1], endpoint='TOF-DEF321.POWER1') # find_one() returns None if record is not found *
        print (data)
        if (data is None or 'id' not in data):   # existence test!
            print ('The device does not exist.\n')
        else:
            print (len(data), ' fields')
            target_id = data['id']
            self.table.update (dict(id=target_id, endpoint='WXY007.POWER1'), ['id'])
            print ('Device end point updated.\n')
            
        print ('Trying to update a non existent device...')
        self.table.update (dict(intofid='IN-9009', endpoint='PQR123.POWER1', fname='cooler'), ['intofid', 'endpoint'])
        print ('Done! nothing happened.\n')          
#-----------------------------------------------------------------------------------------
# MAIN
#-----------------------------------------------------------------------------------------

if (__name__ == '__main__'): 
    print ('initializing database..') 
    
    # format of database url is "dialect://user:password@host:port/dbname" 
    # The following enviroment variable is to be set if you specify 'None' for database_url:
    # SET DATABASE_URL=sqlite:///temp.db
    
    #database_url = None                        # set the URL in the environment
    #database_url = 'sqlite:///temp.db'          # local file
    #database_url = 'sqlite:///:memory:'        # ephemeral; useful for testing
    database_url = Config.DATABASE_URL         # take it directly from config.py file, not app.config
    
    print ('Using database: ', database_url)
    if database_url:
        db = dataset.connect (database_url) 
    else:
        db = dataset.connect()  # setup an environment variable named DATABASE_URL (defaults to :memory:)
    print ('Existing tables: ', self.db.tables)

    relsen_map = RelsenMap (db)
    
    # You must always call setup(). This is where the table is created
    table_exists = relsen_map.setup() 
    
    if (not table_exists):
        print ('Relsen mapping table not found. Creating test entries anyway..')
        relsen_map.add_test_data()
    print()
        
    dev = {
        'intof_id' : test_ids[2], 'device_id' : 'TOF-DDE876', 'relsens' : 
        {'relay1' : 'table lamp', 'relay2' : 'table fan', 'relay3' : 'portico light', 'relay4' : 'power plug' }
    }
    relsen_map.upsert_device (dev)
    print()
    relsen_map.print_stats()
    print()
        
    relsen_map.print_all_data()
    print()
    
    print ('Testing updates..')
    relsen_map.test_update()
    print ('Updates completed.')
    
    relsen_map.print_all_data()
    print()
        
    # Filter   
    iid = 'IN-1001'
    print ('Searching for Intof id: ',iid)
    rels = relsen_map.get_user_records (iid)
    print ('Users records:')
    relsen_map.print_filtered_data (rels)
    print()
        
    iid = 'IN-2002'
    print ('Searching for Intof id: ',iid)
    rels = relsen_map.get_user_relsens (iid)
    print ('Users relsens:')
    print (rels)
    print()
            
    print ('Searching for non-existent user:')
    user = relsen_map.get_user_relsens ('None-Such')
    print ('Users relsens:')
    relsen_map.print_filtered_data (rels)
    print()
    