# parse multiple file URLs, separate author name and title
# new in this version: the input must be a CSV file; TODO:  merge with the XLS version and 
#     read either file format
# https://stackoverflow.com/questions/7372716/parsing-excel-documents-with-python
# Assumption: the script and the data file are in the same directory.
# Assumption : the URL format is:
# file://D:\Amma\804\Author-Title.extn
# The file is a CSV/XLS file where the URL is the 4th column
# Input/Output file format:
# column1 : author
# column2 : title
# column3 : y or n (read or not) 
# column4 : local file path

# pip install xlrd
# pip install xlwt

import os, sys
import csv
import xlrd
import xlwt
from urllib.parse import unquote

#-------------------------------------------------------------------------------------------------
def parse_book_url (book_url):

    col = book_url.split ('\\')[-1]      # the file name is after the last back slash
    sp = col.split ('-')                 # book title is separated by a hyphen from author name
    if (len(sp) < 2):                    # it may be a script file or batch file name found in the folder
        return None
    author = unquote (sp[0]).lower()
    fname = unquote (sp[1]) 
    for i in range (2, len(sp)):         # there may be hyphens within the title; keep them 
        fname = fname + '-' + sp[i]
    fname = unquote (fname)              # there may be an url encoding *after* a hyphen
    title = os.path.splitext (fname)[0]  # remove the file extension 
    return ([author, title])

#-------------------------------------------------------------------------------------------------

def process_file (in_file_name, out_file_name):

    file_error = False
    try :    
        print ('Opening file: ', in_file_name)
        with open (in_file_name, 'r') as f:
            line_count = 0
            reader = csv.reader (f)
            for row  in reader:
                line_count = line_count+1
            print ('Final line number: ', reader.line_num)
        print ('Number of rows found: ', line_count)
    except Exception as e:
        print ("Cannot red input file: " +str(e))
        file_error = True
    if (file_error):
        print ("Quitting ..!")    
        # TODO: close input file?
        sys.exit (1)
        
    try:
        out_workbook = xlwt.Workbook()
        out_sheet = out_workbook.add_sheet ('Sheet1')
    except Exception as e:
        print ("Cannot create output file: " +str(e))
        file_error = True
    if (file_error):
        print ("Quitting ..!")    
        # TODO: close output file?
        sys.exit (1)
           
    # read input rows and parse            
    out_row = 0         
    with open (in_file_name, 'r') as f:
        reader = csv.reader (f)
        r = -1
        for row  in reader:
            try:
                r = r+1
                if (r == 0):  # the first row is a header, ignore it
                    continue
                if (len(row) < 3):  # csv has 3 columns
                    print ('* Invalid row *')
                    continue
                url = row[2]  # third colum has the url
                auth_title = parse_book_url (url)
                if (auth_title is None):
                    print (r, ']  ***')
                    continue
                print (r, '] ', auth_title[0], ' ->  ', auth_title[1])      
                # write output row       
                out_sheet.write(out_row, 0, auth_title[0])
                out_sheet.write(out_row, 1, auth_title[1])
                out_sheet.write(out_row, 2, ' ')         # leave the y or n column blank
                out_sheet.write(out_row, 3, url)
                out_row = out_row + 1  
            except Exception as e:
                print (str(e)) # but the loop continues            
            
    # save output file     
    out_workbook.save (out_file_name)
    print ('\nFile saved as: ', out_file_name)
    # out_workbook.close() ????
 
#----- MAIN ---------------------------------------------------------------------------------------
                
directory =  '.'
if (len(sys.argv) > 1):
    directory = sys.argv[1]
    
print ('\nFolder: ', directory)
print ('Files of type csv : ')   # or xls:')

for filename in os.listdir (directory):
    if filename.endswith(".csv"):   #  or filename.endswith(".xls"):
        in_file_name = os.path.join(directory, filename)
        sp = os.path.splitext (filename)
        out_file_name = os.path.join(directory, 'new_' +sp[0] +'.xls')
        print (in_file_name)
        print (out_file_name)
        process_file (in_file_name, out_file_name)
        print ('-----------------------------------------------------------------------')
        
    