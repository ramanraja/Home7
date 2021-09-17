This is the minimal required libraries/environment to run a program using DataSet abstraction layer on top of MariDB (MySql) database
This package was created such that it can be zipped and uploaded to AWS as a lambda.

Before uploading, run delfiles.py to remove all the cached files.  (Remember to exclude delfiles.py from the zip !)

 Directory of E:\~\lambda_env_package

17-09-21  07.14 PM             3,692 lambda_function.py
17-09-21  07.26 PM               326 README.txt

17-09-21  07.02 PM    <DIR>          alembic
17-09-21  07.02 PM    <DIR>          banal
17-09-21  07.02 PM    <DIR>          dataset
17-09-21  07.02 PM    <DIR>          importlib_resources
17-09-21  07.02 PM    <DIR>          mako
17-09-21  07.02 PM    <DIR>          pymysql
17-09-21  07.21 PM    <DIR>          sqlalchemy
17-09-21  07.21 PM    <DIR>          sqlalchemy_utils