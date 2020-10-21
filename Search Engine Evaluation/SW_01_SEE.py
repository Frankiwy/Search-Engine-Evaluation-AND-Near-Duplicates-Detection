
# coding: utf-8


from bs4 import BeautifulSoup
import csv
import pandas as pd
import os
import time
from collections import defaultdict
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import StemmingAnalyzer,StandardAnalyzer, RegexAnalyzer,SimpleAnalyzer,FancyAnalyzer, NgramAnalyzer,KeywordAnalyzer,LanguageAnalyzer
from whoosh import index
from whoosh.qparser import *
from whoosh import scoring

####################################################################
# PART 1 - Import the .html files and store both into .csv files #
####################################################################
start = round(time.time(),1)

#paths = ["C:./Cranfield_DATASET/DOCUMENTS/", "C:./Time_DATASET/DOCUMENTS"] # paths of the two datasets


def get_csv(path,l,*notitle):
    '''
    The function is used to create a .csv file per each DATASET (Cranfield, Time)
    Function take in input:
        :param path: the path where the .html files are stored
        :param l: the number of docs
        :param notitle: arbitrary value (notitle) to specify if we don't want to consider the title
    '''

    if notitle: # setted as condition for Time .html files where we want to discard the title tag.
        cols = ['ID','body'] # if Time html files inizialize dataframe with 3 columns
    else:
        cols = ['ID','title','body'] # if Cranfiled html files inizialize dataframe with 3 columns

    dataframe = pd.DataFrame(columns=cols)  # inizialize the df where we'll store all the info

    for n in range (1,l+1):

        docfile = path+'_'*6+str(n)+'.html'  # take .html page
        with open(docfile) as d: # open it
            file=d.read() # read it

        soup = BeautifulSoup(file, 'html.parser')  # take in input the .html page and parse it.
        title = soup.title.string.replace("\n", " ")  # take the title under the <title> tag.
        body = soup.body.string.replace("\n", " ")  # take the body under the <body> tag.

        # add ID, body and title (if required) to the dataframe previuosly defined (dataframe).
        if notitle:
            dataframe = dataframe.append({'ID':n, 'body':body}, ignore_index=True) # for Time .html files 
        else:
            dataframe = dataframe.append({'ID':n, 'title':title, 'body':body}, ignore_index=True) # for Cranfiled .html files
    
    #dataframe
    filename= path.split("_")[0][4:]
    path_where_store = "C:./"+filename+"_DATASET/" # get the path where the .csv file has to be stored
    dataframe.to_csv(path_where_store+filename+".csv", index = False, header=True) # store .csv in selected directory
    print(path.split("_")[0][4:]+".csv created and stored")


print('\n\n')
get_csv("C:./Cranfield_DATASET/DOCUMENTS/",1400)
get_csv("C:./Time_DATASET/DOCUMENTS/", 423, 'notitle')

###########################################
# PART 2 - Different configurations of SE #
###########################################

'''
Here it has been defined and filled every schema that it has been decided to have.
In particular, 8 kind of analyzer have been taken into account:
1) 'StemmingAnalyzer'
2) 'StandardAnalyzer'
3) 'RegexAnalyzer'
4) 'SimpleAnalyzer'
5) 'FancyAnalyzer'
6) 'NgramAnalyzer'
7) 'KeywordAnalyzer'
8) 'LanguageAnalyzer'
'''

def schemas(type_analyzer, path, analyzer_name, csvname, *notitle):

    '''
    The schemas function is used to create 8 different schemas(index) according to the 8 different analyzer

    :param type_analyzer: the chosen analyzer
    :param path: the path where the .csv file is stored [[for Cranfield = "C:./Cranfield_DATASET"] and [for Time = "C:./Time_DATASET"]]
    :param analyzer_name: the name of the analyzer used to create the folder where the index will be stored
    :param csvname: name of the .csv file where are contained all the .html docs (Cranfield.csv, Time.csv)
    :param notitle: if notitle, it means only the body is considered (this is used for Time.csv dataset)
    '''


    # create directory where the schema has to be stored
    schema_path = path+'/inverted_index_'+analyzer_name
    os.mkdir(schema_path) # here the directory is created per each Analyzer


    selected_analyzer = type_analyzer #the chosen analyzer

    if notitle: #define schema for Time dataset
        schema = Schema(id = ID(stored=True), 
                        body = TEXT(stored=False, analyzer=selected_analyzer))
    else: #define schema for Cranfield dataset
        schema = Schema(id = ID(stored=True),  
                        title = TEXT(stored=False, analyzer=selected_analyzer),
                        body = TEXT(stored=False, analyzer=selected_analyzer))

    create_in(schema_path, schema) # store the schema into the direcory previously created

    ix = index.open_dir(schema_path) #  go inside directory and pick predefined schema

    writer = ix.writer(procs=1) # write inside the inverted index but not in parallel

    ALL_DOCUMENTS_file_name = path+'/'+csvname+".csv" # pick the file
    in_file = open(ALL_DOCUMENTS_file_name, "r", encoding='latin1') # open it
    csv_reader = csv.reader(in_file, delimiter=',') # read it
    csv_reader.__next__()  # to skip the header: first line containing the name of each field.
    num_added_records_so_far = 0 #counter used to show the progress
    
    for record in csv_reader:
        id = record[0] #pick the ID
        
        if notitle: # for Time.csv we don't have the title,so:
            body = record[1]
            writer.add_document(id=id, body=body)
        else:# for Cranfield.csv we have title, so:
            title = record[1]
            body = record[2]
            writer.add_document(id=id, title=title, body=body)  # we are indexing one doc at time
        #

        #
        num_added_records_so_far += 1
        if (num_added_records_so_far % 100 == 0):
            print(" num_added_records_so_far= " + str(num_added_records_so_far))
    #
    writer.commit()  # it is necessary to store the index once filled
    in_file.close()  # it is necessary to close the .csv file


'''
Here "schemas" function is used to create and fill all the schemas(indexes) for both .csv files (Cranfield.csv and Time.csv)

'''

analyzers = [StemmingAnalyzer(), StandardAnalyzer(), RegexAnalyzer(), SimpleAnalyzer(),
             FancyAnalyzer(), NgramAnalyzer(4), KeywordAnalyzer(), LanguageAnalyzer('en')] # all the analyzers that are used
analyzer_names = ['StemmingAnalyzer', 'StandardAnalyzer', 'RegexAnalyzer', 'SimpleAnalyzer',
                 'FancyAnalyzer', 'NgramAnalyzer', 'KeywordAnalyzer',  'LanguageAnalyzer'] # analyzers names

csv_names = ['Cranfield', 'Time'] # file names



# start to iterate over all the .csv files (in particular the only two that there are, Cranfield.csv, and Time.csv)
for name in csv_names: 
    
    print(name, '\n\n')
    
    path = "C:./"+name+"_DATASET" # get the path where the .csv is stored
    for e,type_analyzer in enumerate(analyzers): # now the iteration is necessary to create the 8 different inverted indexes
        
        print('Analyzer: '+analyzer_names[e])
        if name == 'Time': # because Time.csv doesn't have the title (because it hasn't been considerd) the schema does not require title field:
            schemas(type_analyzer, path, analyzer_names[e], name, 'notitle') # generate and write inside every schema, based on the selected Analyzer
        else: # because Cranfield.csv has the title field, it must be considered
            schemas(type_analyzer, path, analyzer_names[e], name)
        print('\n')
    print('\n\n')





##########################################################################################
# PART 3 - Evaluate every query based on different index and different scoring function. #
##########################################################################################

'''
This is the last PART of SW_01 where, at the end 24 different Search Engines are retrieved.
The Search Engines will be 24 because there are 8 different schemas(indexes), and per each schemas(indexes) 3 different scoring functions have been used.
    - Selected Scoring Functions = [TF_IDF, Frequency, BM25F]

Once the 24 SEs have been returned, they'll be stored into .tsv files that will be used by SW_02 to evaluate the SEs themselves.
'''


def query_evaluator(file_directory,query_tsv_name,result_limit, *notitle):
    '''
    This function is used to evaluate all queries by the 24 different Search Engine.
    :param file_directory: directory where the indexes are stored ("C:./Cranfield_DATASET/" and "C:./Time_DATASET/" )
    :param query_tsv_name: Queries.tsv names (cran_Queries.tsv, time_Queries)
    :param result_limit: the number of top k results retrieved
    :param notitle: if notitle, it means only the body is considered (this is used for Time.csv dataset)
    :return: SEs = that is a dictionary where the keys are the Search Engines (ex. SE_01, SE_02, ..., SE_24) and the values their query document results
    '''


    SEs = defaultdict(list) # dictionary where all the SEs will be stored
    query_path = file_directory+query_tsv_name # query_path = path where there are the queries ["C:./Cranfield_DATASET/cran_Queries.tsv", "C:./Time_DATASET/time_Queries.tsv"]
    
    analyzer_names = ['StemmingAnalyzer', 'StandardAnalyzer', 'RegexAnalyzer', 'SimpleAnalyzer',
                      'FancyAnalyzer', 'NgramAnalyzer', 'KeywordAnalyzer',  'LanguageAnalyzer'] # analyzers names
        
    counter = 1 # counter used to name the SEs
    for analyzer in analyzer_names: 

        index_directory = file_directory+'inverted_index_'+analyzer #get the directory where the index is stored

        ix = index.open_dir(index_directory) # open the index inside the chosen directory
        scoring_functions = [scoring.TF_IDF(),scoring.Frequency(),scoring.BM25F(B=0.75,K1=1.2)] # list of chosen scoring functions

        # per each index three different scoring functions are used:
        for score in scoring_functions:

            scoring_function = score # select the scoring function

            if notitle: #this is fot Time dataset because only the body will be considered
                # query parser
                qp = QueryParser("body", ix.schema) # here we are telling to the search engine in which fields it has to perform the query, if we use multifield we search in more than one field.
            else: # this is for the Cranfield dataset because both title and body will be considered
                # query parser
                qp = MultifieldParser(["title","body"], ix.schema) # here we are telling to the search engine in which fields it has to perform the query, if we use multifield we search in more than one field.


            # Create the searcher for the index based on the predefined scoring function
            searcher = ix.searcher(weighting=scoring_function)

            with open(query_path) as tsvfile: # here the .tsv containing the query is used and one by one are parsed
                querys = csv.reader(tsvfile, delimiter='\t')
                header = next(querys) # check if there is the header 
                if header != None: # if there is the header iterate over all the rows in the Query.tsv file (cran_Queries.tsv, time_Queries)
                    for query in querys:
                        parsed_query = qp.parse(query[1])  # parsing the query (because up to now, the query is just a python string, and it has to be interpreted by the program. Because up to now it's just a boolean operator)
                        results = searcher.search(parsed_query, limit=result_limit) # here the query is performed and only the top "result_limit" will be considered

                        for hit in results:
                            '''
                            here the relevant results will be selected. In particular:
                            Query number, Doc ID, Rank and Score
                            '''
                            output = [query[0],hit['id'], str(hit.rank + 1), str(hit.score)]
                            SEs['SE_'+str(counter)].append(output) # the results are added to the predefined dictionary
            print('analyzer: '+analyzer, 'scoring_function: '+str(scoring_function).split('.')[2].split(' ')[0], '('+str(counter)+')')
            counter +=1
    return(SEs)


'''
Here the "query_evaluator" function is run for both datasets: 
'''

print('\n', 'Search Engines Cranfield')
SE_Cranfield = query_evaluator("C:./Cranfield_DATASET/","cran_Queries.tsv", 40)
print('\n', 'Search Engines Time')
SE_Time = query_evaluator("C:./Time_DATASET/","time_Queries.tsv", 40, 'notitle')



'''
The function below is used to store the SE results into different .tsv files (in total 24)
'''

def SE_tsv_writer(SE,path):

    '''
    This is the function used to store the SEs results into .tsv files
    :param SE: is a dictionary where:
                SE = {SE_1: [['Query_id', 'Doc_id', 'Rank', 'Score']
                             ['Query_id', 'Doc_id', 'Rank', 'Score']
                       ...]
                      SE_2: [['Query_id', 'Doc_id', 'Rank', 'Score']
                       ...]
                     ...
                     SE_24: [...]
                     }
    :param path: is the path used to create the directory where all the SEs, previously difined and used as input of this functions (SE), will be stored
                    - "C:./Cranfield_DATASET/"
                    - "C:./Time_DATASET/"
    '''

    keys = [k for k in SE.keys()] # list with all the SE names
    folder_name = path+'/SEs_results' # path where to create the folder where store all the SE_n.tsv results
    os.mkdir(folder_name)  # create the folder
    
    # per each SE, save it into .tsv file
    for key in keys:
        with open(folder_name+'/'+key+'.tsv', 'wt') as out_file:
            tsv_writer = csv.writer(out_file, delimiter='\t')
            tsv_writer.writerow(['Query_id', 'Doc_id', 'Rank', 'Score']) # add header to .tsv file
            for row in SE[key]: # add every row to the .tsv file
                tsv_writer.writerow(row)
        print(key+' stored into: '+path)

print('\n', 'Start storing Search Engines Cranfield into .tsv files:')
SE_tsv_writer(SE_Cranfield,"C:./Cranfield_DATASET")
print('\n', 'Start storing Search Engines Time into .tsv files:')
SE_tsv_writer(SE_Time,"C:./Time_DATASET")

end = round(time.time(),1)
print('total time: '+str(round((end-start)/60,))+' minutes')
