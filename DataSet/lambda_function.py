# DataSet - a simple data abstraction layer over SQLAlchemy
# Hosting this on AWS Lambda
# Zip all the dependencies of DataSet and upload. See README.txt

# https://dataset.readthedocs.io/en/latest/
# MySQL driver work around:
# https://stackoverflow.com/questions/53024891/modulenotfounderror-no-module-named-mysqldb

# pip install dataset

import json
import pymysql
pymysql.install_as_MySQLdb() # this is a work around to make pymysql work with Python 3.x
import dataset

# format of database url is "dialect://user:password@host:port/dbname" 

#db = dataset.connect ('sqlite:///temp.db')  # triple slash to denote it is on the local folder
#db = dataset.connect ('sqlite:///:memory:')
db = dataset.connect ("mysql://username:passwd@100.101.102.103:3306/customerdb")
print (type(db))

def lambda_handler(event, context):

    citizen_table = db['citizens']  # the table name, as far as the DB is concerned, is 'citizens'
    print (type(citizen_table))
    
    usr1 = dict(name='Bruce Lee', age=28, country='China', job='fighter')
    usr2 = dict(name='Ching Ming', age=44, country='china', gender='male')  # 'China' and 'china' are different countries; case matters!
    usr3 = dict(name='John Doe', age=37, country='France', gender='female')
    # json
    usr4 = {'name' : 'Jack ripp', 'age' : 17, 'country' : 'France', 'job' : 'stenographer'}
    usr5 = {'name' : 'Paul Doe', 'age' : 65, 'country' : 'USA', 'gender' : 'female'}
    
    citizen_table.insert (usr1)
    citizen_table.insert (usr2)
    citizen_table.insert (usr3)
    print ('3 users added.')
    
    
    # use 'name' as search filter and update that row
    citizen_table.update (dict(name='John Doe', age=99), ['name'])
    
    # Transaction
    db.begin()
    try:
        citizen_table.insert (usr4)
        citizen_table.insert (usr5)    
        db.commit()
        print ('2 rows added')
    except Exception as e:
        print ('Exception: ' +str(e))
        db.rollback()
        
    # Get all table names
    print ('Tables in the db:')
    print (db.tables)
    # Number of rows
    print ('Row count: ', len(citizen_table))
    
    
    # get columns
    print ('Columns in the table:')
    print(db['user'].columns)
    
    # Aliter:
    print(citizen_table.columns)
    
    # Read data
    print ('Your data:')
    data = citizen_table.all()
    print (type(data))
    ###print (len(data)) # error
    print (data)  
    
    
    for row in citizen_table:
        print (row['name'],  ' -> ', row['age'])
    
    
    # Filter   
    data = citizen_table.find_one (name='John Doe') # it is a single '=', not '==' 
    print ('Found John!')
    print (type(data))
    print (data)  # prints one record correctly
    
    
    print ('French speakers:')
    data = citizen_table.find (country='France')  
    print (type(data))
    print (data)  # it is a collection object, you have to iterate
    for d in data:
        print (d)
    
        
    print ('Senior citizens:')
    #data = citizen_table.find ((age, '>=', 60)) # error: 'age' is undefined
    # Use the underlying SQLAlchemy directly
    data = citizen_table.find (citizen_table.table.columns.age >= 60)
    for d in data:
        print (d)
    
    
    print ("All Doe's:")
    data = citizen_table.find (name={'like': '%Doe%'})
    for d in data:
        print (d)
    
    
    # Aggregate
    print ('Counts:')
    query_str = 'SELECT country, COUNT(*) cnt FROM citizens GROUP BY country'
    result = db.query (query_str)
    for row in result:
       print(row['country'], row['cnt'])
   
 
    return {
        'statusCode': 200,
        'body': json.dumps('Good job, DataSet !')
    }   
