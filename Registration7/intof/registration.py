# registration.py
# Backend code to add Intof customers to the Intof database
# pip install dataset

# TODO: API for update, delete
# TODO: factor out the common code to a base class (feature:instead of iterator, bulk downloads as a list)

from urllib.request import urlopen
from collections import OrderedDict
import pymysql
from random import randint
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset
import json
from intof.testids import test_ids
from config import Config
#---------------------------------------------------------------------------------------------------------------

class UserRegistration ():

    def __init__ (self, database):
        self.db = database
        self.table_name = 'registration'   # it is case sensitive *
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
                     
                     
    def get_user (self, intof_id):
        record = self.table.find_one (intofid=intof_id) # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'intofid' not in record):
            return None
        return record # This always returns a singleton  
     
    def does_user_exist (self, intof_id):
        if (self.get_user (intof_id) is None):
            return False
        return True

        
    def intof_email_map (self, intof_id):
        record = self.table.find_one (intofid=intof_id)   # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'email' not in record):
            return None
        return (record['email'])  # This always returns a singleton  
        
        
    def email_intof_map (self, email_id):
        record = self.table.find_one (email=email_id)   # returns None if recrod is not found
        #print (record)
        #print (type(record))
        if (record is None or 'intofid' not in record):
            return None
        return (record['intofid'])  # This always returns a singleton  
        
     
    def does_email_exist (self, email_id):
        if (self.email_intof_map (email_id) is None):
            return False
        return True
        
        
    def create_user (self, user): 
        print ('Adding a new user: ', user)
        if  'email' not in user:        
            return {'success' : False, 'msg' : 'Email is required'}
        existing_mail = self.email_intof_map (user['email'])
        if (existing_mail is not None) :
            return {'success' : False, 'msg' : 'Email already exists'}
        mail = user.get('email')  # Assumption: the mail format has been validated by the front end
        if  'intofid' not in user:        # TODO: revisit this design choice
            iid = self.create_intof_id()  
        else:
            iid = user.get('intofid')
        print ('Intof id of new user: ', iid)
        if  'password' not in user:
            passwd = self.create_default_password()
        else:
            passwd = user.get('password') 
        name = user.get('name', 'NO-NAME')  # TODO: do input validation of these!
        phash =  self.create_password_hash (passwd)
        user_record = {'intofid' : iid, 'email' : mail, 'name' : name, 'passhash' : phash}
        try:
            self.table.insert (user_record)  
        except Exception as e:
            return {'success' : False, 'msg' : str(e)}    
        return {'success' : True, 'msg' : 'User created.', 'intof_id' : iid}
    
    
    def create_intof_id (self):
        r = randint(10000,1000000)   
        iid = 'IN-' +str(r)
        print (f'Random user id: {iid}')
        if self.does_user_exist (iid): # duplicate id; try again
            print ('** Duplicate id generated! Trying again..')
            return self.create_intof_id()  
        return (iid)
        
        
    def create_default_password (self):
        default_passwd = 'intof'  # TODO: implement randomized password
        return  (default_passwd)  
        
        
    def create_password_hash  (self, passwd):
        return (passwd[::-1])     # TODO: implement
        
    
    # ---------------- utility helpers ------------------------------------------
        
    def add_test_data (self):
        usr1 = dict(intofid=test_ids[0],  email='raj@aman.com', name='Raman Raja', passhash='ACASDFK234ASDFO09')
        usr2 = {'intofid' : test_ids[1], 'email' : 'jara@maran.com', 'name' : 'Jara Maran', 'passhash' : 'TT4894KI40XX'}
        usr3 = {'intofid' : test_ids[2], 'email' : 'kittu@mama.com', 'name' : 'Kittu Mama', 'passhash' : 'YY90UI34KJ5R'}
        usr4 = {'intofid' : test_ids[3], 'email' : 'pattu@mami.com', 'name' : 'Pattu Mami', 'passhash' : 'XX6996XX6996'}
        usr4 = {'intofid' : test_ids[4], 'email' : 'rik@kut.com', 'name' : 'Pak Man', 'passhash' : 'XX6996XX6996'}
        usr4 = {'intofid' : test_ids[5], 'email' : 'app@pulu.com', 'name' : 'Jala pino', 'passhash' : 'XX6996XX6996'}        
        usr4 = {'intofid' : test_ids[6], 'email' : 'vk@intof.com', 'name' : 'Pina colada', 'passhash' : 'XX6996XX6996'}        
        self.table.insert (usr1)
        self.table.insert (usr2)
        self.table.insert (usr3)
        self.table.insert (usr4)
        print ('7 test users added.')
    
    
    def print_all_data (self):
        print ('Your data:')
        for row in self.table:  # the table object has a built in iterator. Cool!
            print ('  ({}) {} -> {}, {} [{}]'.format(row['id'], row['intofid'],row['email'],row['name'],row['passhash']))  #[:10]))
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
    print ('Existing tables: ', db.tables)
    
    user_reg = UserRegistration (db)
    
    # You must always call setup(). This is where the table is created
    table_exists = user_reg.setup() 
    
    if (not table_exists):
        print ('User mapping table not found. Creating test entries anyway..')
        user_reg.add_test_data()
    print()
        
    usr = {
        'name' : 'Apputtu',
        'age' : 11   # irrelevant field, ignored
    }    
    result = user_reg.create_user (usr)
    print (result)
    print()
    
    usr = {
        'name' : 'Apputtoo',
        'email' : 'app@ttoo.com'
    }    
    result = user_reg.create_user (usr)
    print (result)
    print()
        
        
    user_reg.print_all_data()
    print()
    user_reg.print_stats()
    print()
    
    # Filter   
    iid = 'IN-1001'
    print ('Searching for Intof id: ',iid)
    user = user_reg.get_user (iid)
    print ('User profile:')
    print (user)
    print()
        
    print ('Searching for non-existent user:')
    user = user_reg.get_user ('None-Such')
    print ('User profile:')
    print (user)
    print()