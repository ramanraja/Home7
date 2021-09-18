# DataSet - a simple data abstraction layer over SQLAlchemy 
# https://dataset.readthedocs.io/en/latest/
# MySQL driver work around:
# https://stackoverflow.com/questions/53024891/modulenotfounderror-no-module-named-mysqldb
# There is no way of explicitly shutting down the connection; the dataset instance will be garbage collected.

# pip install dataset

import pymysql
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset
from collections import OrderedDict

# Globals

# format of database url is "dialect://user:password@host:port/dbname" 
#db = dataset.connect() # setup an environment variable named DATABASE_URL (defaults to :memory:)
#db = dataset.connect ('sqlite:///temp.db')  # triple slash to denote it is on the local folder
#db = dataset.connect ("mysql://user:passwd@100.101.102.103:3306/customers")
db = dataset.connect ('sqlite:///:memory:')

print (type(db))

citizen_table = db['citizens']  # the table name, if created new, will be 'citizens'
# Aliter: if the table already exists, you can use load_table('citizens')
print (type(citizen_table))

#---------------------------------------------------------------------------------------------

def add_data():
    # dictionary
    usr1 = dict(name='Bruce Lee', age=28, country='China', job='fighter')
    usr2 = dict(name='Ching Ming', age=44, country='china', gender='male')  # 'China' and 'china' are different countries; case matters!
    usr3 = dict(name='John Doe', age=37, country='France', gender='male')
    # json
    usr4 = {'name' : 'Jack Doe', 'age' : 17, 'country' : 'France', 'job' : 'stenographer'}
    usr5 = {'name' : 'Priyanka', 'age' : 65, 'country' : 'India', 'gender' : 'female', 'job':'nurse'}
    usr6 = {'name' : 'Priyanka', 'age' : 15, 'country' : 'India', 'gender' : 'female'}     # duplicate name
    
    citizen_table.insert (usr1)
    citizen_table.insert (usr2)
    citizen_table.insert_many ([usr3, usr4]) # bulk upload
    
    # Transaction
    db.begin()
    try:
        citizen_table.insert (usr5)
        citizen_table.insert (usr6)
        db.commit()
        print ('Txn: 2 rows added')
    except Exception as e:
        print ('Exception: ' +str(e))
        db.rollback()
    print ('6 users added.\n')


def print_all_data():
    print ('Your data:')
    for row in citizen_table:  # the table object has a built in iterator. Cool!
        print ('  {} ({}, {}) -> {}, {}'.format(row['name'],row['gender'],row['age'],row['country'],row['job']))
    print ('Total rows: ', citizen_table.__len__())
    print ('-'*25)


def print_filtered_data (data):
    count = 0
    print (type(data))  # this may be a result iterator (possibly, of length 0,1 or more)
    print (data)        # if data is a collection object, you have to iterate through it
    ##if hasattr (data, '__iter__'): # it is an iterable object
    if isinstance (data, dataset.util.ResultIter):
        for d in data:
            print (d)
            count += 1
    elif isinstance (data, OrderedDict):
        count = 1
    print ('Filtered rows: ', count)
    print ('-'*25)
    return count
#---------------------------------------------------------------------------------------------
# MAIN
#---------------------------------------------------------------------------------------------

add_data()
print_all_data()

# use 'name' as search filter and update that row, IF FOUND
# If you dont want to update over a particular value, just use the auto-generated id column.
citizen_table.update (dict(name='John Doe', age=99), ['name'])
print ('After the update:')
print_all_data()

# upsert() = create a new row if not existing
new_data = dict(name='Rajaram', age=88, gender='male', country='India')
citizen_table.upsert (new_data, ['name'])
print ('After the upsert:')
print_all_data()
# update the upserted row
new_data = dict(name='Rajaram', age=89, job='retired')
citizen_table.upsert (new_data, ['name'])
print ('After the update:')
print_all_data()

# Filter   
data = citizen_table.find_one (name='John Doe') # it is a single '=', not '==' 
print ('Found one John! id={}'.format(data['id']))
print_filtered_data (data) # this is an ordered dictionary

data = citizen_table.find (name='Bruce Lee')  
print ('Found Bruce(s)!')
print_filtered_data (data)

print ('Trying to print non existent entities!..')
data = citizen_table.find (name='Non-exist')  
row_count = print_filtered_data (data)
if (row_count==0):
    print ('No records found.\n')
    
print ('Found Priyankas..!')
data = citizen_table.find (name='Priyanka')  
print_filtered_data (data)

target_id = None
data = citizen_table.find (name='Priyanka')  # the previous iterator has already reached its end ! ***
for d in data:
    print (d['id'], d['name'], d['age'])
    if d['age']==15:
        target_id = d['id']
print ('Target id of Priyanka to be updated: ',target_id)
if (target_id is not None):        
    print ('Updating Priyanka with id ', target_id)
    newjob = dict(id=target_id, job='student')
    citizen_table.update (newjob, ['id'])
    data = citizen_table.find (name='Priyanka')  
    print_filtered_data (data)

print ('Distinct countries:')
data = citizen_table.distinct ('country')
print_filtered_data (data)

print ('All French citizens:')
data = citizen_table.find (country='France')  
print_filtered_data (data)
    
print ('All French or Indian citizens:')
data = citizen_table.find (country=('France','India')) 
print_filtered_data (data)
    
print ('All French stenographers:')
data = citizen_table.find (country='France', job='stenographer')  
print_filtered_data (data)    
   
print ('All [cC]hinese citizens:')
data = citizen_table.find (country={'ilike' : 'china'})   # ilike = case insensitive search
print_filtered_data (data)

print ("All ending with 'a' citizens:")
data = citizen_table.find (country={'like' : '%a'})    
print_filtered_data (data)

print ('All senior citizens:')
data = citizen_table.find (age={'>=' : 60})    
print_filtered_data (data)

print ('Filter using raw SQL - all French:')
sql_statement = "SELECT * FROM citizens WHERE country='France'"
data = db.query (sql_statement)
print_filtered_data (data)

# For delete, the filter criterion will always be equality
print ('Deleting all males..')
citizen_table.delete (gender='male')
print_all_data()

print ("Deleting all the genderless..")
citizen_table.delete (gender=None)
print_all_data()









