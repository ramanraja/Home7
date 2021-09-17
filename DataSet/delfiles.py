# iteratively delete __pycache__ directories and their content
# https://stackoverflow.com/questions/18394147/recursive-sub-folder-search-and-return-files-in-a-list-python
# https://www.geeksforgeeks.org/delete-a-directory-or-file-using-python/
 
import os 
import glob

base_dir = 'E:\NewRaja1\Work2\Python\I\Database\lambda_env_package'
base_pattern = base_dir + '/**/__pycache__'

# iglob returns an iterator

print ('deleting all __pycache__ folders under ', base_dir)
fcount = 0
dcount = 0
for current_dir in glob.iglob (base_pattern, recursive=True):
    print (current_dir)    
    current_pattern = current_dir +'/**'
    for f in glob.iglob (current_pattern, recursive=True):
        print ('\t', f)
        if not os.path.isdir(f):
            os.remove (f)
            fcount += 1
    os.rmdir (current_dir)
    dcount += 1
    
print ('\nDeleted {} files in {} directories'.format (fcount,dcount))
    