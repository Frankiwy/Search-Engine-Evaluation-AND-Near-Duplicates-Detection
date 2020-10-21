
# coding: utf-8

# # SW_2

import csv
from collections import defaultdict
import math
import time
import numpy as np
import matplotlib.pyplot as plt 

start = time.time()

#########################
# IMPORT SEARCH ENGINES #
#########################
def import_SE_and_GT(GT_path, SEs_path):

    '''
    The function takes in input:
    :param GT_path: path where the ground truth is stored:
                    - "./Cranfield_DATASET/cran_Ground_Truth.tsv"
                    - "./Time_DATASET/time_Ground_Truth.tsv"
    :param SEs_path: where the Search Engines are stored
                    - "./Cranfield_DATASET/SEs_results/
                    - "./Time_DATASET/SEs_results/"
    :return: two dictionaries, one for the Ground Truth and another one with all Search Engines.
    '''

    # ground truth dictionary computation
    ground_truth = defaultdict(set)

    with open(GT_path) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        next(tsvreader)
        for line in tsvreader:
            ground_truth[int(line[0])].add(int(line[1]))


    # engine dictionary computation
    engines = defaultdict(dict)
    for n in range(1,25):
        with open(SEs_path+"SE_"+str(n)+".tsv") as tsvfile:
            tsvreader = csv.reader(tsvfile, delimiter='\t')
            next(tsvreader)
            engine=defaultdict(list)
            for e,line in enumerate(tsvreader):
                if (e % 2) == 0: #even lines have to be skippend because empthy. This is due to that fact that when the .tsv file have been generated, an empthy line after every input have benne added
                    continue
                else:
                    if int(line[0]) not in [gt for gt in ground_truth.keys()]: # check if the query is in the GT. If it is not, it'll not import.
                        continue
                    else:
                        engine[int(line[0])].append(int(line[1]))
            engines['SE_'+str(n)] = engine
    
    return(ground_truth, engines)

########################
# Mean Reciprocal Rank #
########################

def MRR_function(engines, GT):

    '''
    The function is used to compute the MeanReciprocalRank for all the Search Engines.
    The function takes in input:
    :param engines: dictionary with all the Search Engines and their results
    :param GT: ground Truth
    :return: MRR
    '''

    MRR = dict() # dictonary where will be stored all the MRR for each SE

    for SE in engines.keys(): # iteration over all the SE
        
        RR_results = list()
        
        for query in engines[SE]: # per each query associated to each SE

            query_result = list() 

            for e,DOC_ID in enumerate(engines[SE][query]): # per each DOC_id it is checked if it is the ground Thruth
                if DOC_ID in GT[query]: # if it is
                    query_result.append(1/(e+1)) # the RR is computed

                else:
                    continue # else it is skipped

            if len(query_result) == 0: # if there are no results a 0 is add as RR result for the given query
                RR_results.append(0)
            else: #else, only the first result is taken and added to the dictionary
                RR_results.append(query_result[0]) 
        
        
        MRR[SE] = (sum(RR_results))/len(RR_results)
        

        
    MRR = {k: v for k, v in sorted(MRR.items(), key=lambda item: item[1], reverse=True)} # sort in descending oreder based on the MRR result    
    return(MRR)

###############
# R-Precision #
###############

def R_precision_function(engines, top_5_SE, GT):

    '''
    The function takes in input:
    :param engines: the dictionary where there are all the engines
    :param top_5_SE: dictionary where there are the top 5 SE based on the MRR result
    :param GT: dictionary with the Ground Truth for alla the queries
    :return: R_precison, that is a dictionary where the keys are the SEs and the values the list of R_precision per each query.
    '''

    R_precision = dict() # dictionary where the key is the SE and the value is the list with all R_precions
    for SE in top_5_SE: # iterate over all top 5 SEs

        sum_of_number_of_relevant_doc=list() # list where will be stored all R_precions of selected SE
        for query in engines[SE]:

            number_of_relevant_doc = 0 # counter used to sum up all relevant docs of a SE for a given query
            for DOC_ID in engines[SE][query][:len(GT[query])]: # only the top |GT(q)| retrieved results will be considered
                if DOC_ID in GT[query]:
                    number_of_relevant_doc +=1 #if DOC_ID is in the query, add 1 to the counter
                else:
                    continue
            sum_of_number_of_relevant_doc.append(number_of_relevant_doc/len(GT[query])) # compute the R_precion for the given query and store it


        R_precision[SE] = sum_of_number_of_relevant_doc # associate the list of all R_precisons to a given SE.
    
    
    # print table with Mean, min, 1st Quartile, Median, 3rd Quartile, MAX
    print('-'*94,
          "SE" + "\t" +
          "mean" + "\t\t" +
          "min" + "\t\t" +
          "Q1" + "\t\t" +
          "Median"+ "\t\t" +
          "Q3"+ "\t\t" +
          "max", '-'*94, sep='\n')
    for se,SE_list in R_precision.items():
        print(se + "\t" + 
              str(round(np.mean(SE_list),4)) + "\t\t" +
              str(round(min(SE_list),4)) + "\t\t" +
              str(round(np.percentile(SE_list, 25),4)) + "\t\t" +
              str(round(np.median(SE_list),4))+ "\t\t" +
              str(round(np.percentile(SE_list, 75),4)) + "\t\t" +
              str(round(max(SE_list),4)))
    
    
    
    return(R_precision)

#######
# P@K #
#######

def PaK_function(k_list, engines, top_5_SE, GT):

    '''
    The function takes in input:
    :param k_list: list of chosen k [1,3,5,10]
    :param engines: the dictionary where there are all the engines
    :param top_5_SE: dictionary where there are the top 5 SE based on the MRR result
    :param GT: dictionary with the Ground Truth for alla the queries
    :return: k_scores, that is a dictionary where the keys are the Ks and the values the mean_PaK per each SE.
    '''

    k_scores = dict() # dictionary where all the mean_P@K of each SE will be stored based on the chosen k

    for k in k_list: # iteration over the 4 k
        PaK = dict() # dictionary where the mean_P@k of SEs, based on a given k, will be stored 
        for SE in top_5_SE: # only the top 5 SEs will be considered

            sum_of_number_of_relevant_doc=0 # counter used to sum up all "number_of_relevant_doc" of given SE for all the queries (everything based on the chosen k)
            for query in engines[SE]:

                upto = min(len(GT[query]),k) # pick the minimum among the query lenght and k

                number_of_relevant_doc = 0 # counter used to sum up all relevant docs of a SE for a given query
                for DOC_ID in engines[SE][query][:upto]: # only the top, min(k,|GT(q)|), retrieved results will be considered

                    if DOC_ID in GT[query]:
                        number_of_relevant_doc +=1 # if the doc_id is into the GT add 1 to the counter
                    else:
                        continue
                sum_of_number_of_relevant_doc += number_of_relevant_doc/upto # perform P@k for a given given query and add it to the "sum_of_number_of_relevant_doc" 


            PaK[SE] = sum_of_number_of_relevant_doc/len(GT.keys()) #perform mean_P@k for a given SE based on a given k
        
        k_scores[k] = PaK # store the PaK dictionary into k_scores dictionary
    
    return(k_scores)

#########################################
# normalized Discounted Cumulative Gain #
#########################################

def nDCG_function(k_list, top_5_SE, engines, GT):

    '''
    The function takes in input:
    :param k_list: list of chosen k [1,3,5,10]
    :param top_5_SE: the dictionary where there are all the engines
    :param engines: dictionary where there are the top 5 SE based on the MRR result
    :param GT: dictionary with the Ground Truth for alla the queries
    :return: k_nDCG_scores, that is a dictionary where the keys are the Ks and the values the mean_nDCG per each SE.
    '''

    k_nDCG_scores = dict() # dictionary where all the mean_nDCG of each SE will be stored based on the chosen k

    for k in k_list: # the loop start to iterate over all the possible k

        nDCG_dict = dict() # dictionary where the mean_nDCG of SEs, based on a given k, will be stored

        for SE in top_5_SE:# only the top 5 SEs will be considered

            total_nDCG = 0 # counter used to sum up all the DCG of given SE for all the queries (everything based on the chosen k)

            for query in engines[SE]:
                upto = min(len(GT[query]), k)
                IDCG = sum([1 / math.log2(n + 1 + 1) for n in range(upto)]) # the IDCG per each query is computed.
                # At the denominator of IDCG there is n +1+1 because range method starts counting from 0 so it is necessary add another +1
                DCG = 0 # used to compute the DCG of a given SE result on a specific query
                for e,DOC_ID in enumerate(engines[SE][query][:upto]): # only the top k retrieved results will be considered

                    if DOC_ID in GT[query]: # if the doc_id is into the GT

                        DCG += 1/np.log2(e+1+1) # compute the DCG 
                        # also here, at the denominator, there's e+1+1 because enumerate starts counting from 0
                    else:
                        continue #not compute DCG
                nDCG = DCG/IDCG # once all the k-DOC_ID have been parsed, compute the nDCG for this query
                total_nDCG += nDCG # add the nDCG to the counter that will be used to compute the mean nDCG for a SE based on a given k

            mean_nDCG = total_nDCG/len(GT.keys()) # compute the mean nDCG for the SEs based on the chosen k
            nDCG_dict[SE] = mean_nDCG # add the nDCG to the dictionary

        k_nDCG_scores[k] = nDCG_dict #add all the mean nDCG results of SEs and add them to the k_nDCG_scores that will be used to retrieve all the mean nDCG of SEs based on the k
    return(k_nDCG_scores)


#################
# Plot function #
#################

def plot_function (top_5_SE, method_results, ylabel):

    '''
    The function is used to plot the curves for top 5 SEs.
    The function takes in input:
    :param top_5_SE: dictionary where there are the top 5 SE based on the MRR result
    :param method_results: dictionary with results, it can be k_nDCG_scores or R_precision for both datasets Cranfield ot Time.
    :param ylabel: label on y axis
    :return:
    '''

    plt.figure(figsize=(12, 10))

    SE_k = list() # list where will be stored all the 4 (either nDCG or R_precision) for all top 5 SEs
    for SE in top_5_SE: # iteratio over top 5 SEs
        SE_list = list() # list where will be stored the 4 results related to one SE
        for k in method_results: 
            SE_list.append(method_results[k][SE]) #pick the value for a paritucal SE, given a k
        SE_k.append(SE_list)   

    color_list = ['tomato', 'skyblue', 'seagreen', 'magenta', 'yellow' ]    


    for n in range(len(SE_k)): # plot a curve per each SE
        plt.plot([1,3,5,10], SE_k[n], color = color_list[n], linewidth=4)

    plt.style.use('Solarize_Light2')

    plt.xlabel('k', fontsize=25).set_color("Black")
    plt.ylabel(ylabel, fontsize=25).set_color("Black")


    plt.legend(['SE_24',
                'SE_6',
                'SE_15',
                'SE_3',
                'SE_9'], loc='best', fontsize = 24)

    plt.show()

###########
# RESULTS #
###########

# Here all the results are returned:


GT_Cranfield, engines_Cranfield = import_SE_and_GT("./Cranfield_DATASET/cran_Ground_Truth.tsv", "./Cranfield_DATASET/SEs_results/")
GT_time, engines_Time = import_SE_and_GT("./Time_DATASET/time_Ground_Truth.tsv", "./Time_DATASET/SEs_results/")
print("Cranfield and Time SEs imported...", '\n')


MRR_Cranfield = MRR_function(engines_Cranfield, GT_Cranfield)
print('\n','Cranfield:','\n')
for k,v in MRR_Cranfield.items():
    print('|'+k+'\t'+'|'+'MRR result: '+str(round(v,3))+'|')
MRR_Time = MRR_function(engines_Time, GT_time)
print('\n','Time:','\n')
for k,v in MRR_Time.items():
    print('|'+k+'\t'+'|'+'MRR result: '+str(round(v,3))+'|')


top_5_SE_Cranfield = [k for k in MRR_Cranfield.keys()][0:5]
print('\n', 'Ordered top 5 SEs for Cranfield: ', top_5_SE_Cranfield, '\n')
top_5_SE_Time = [k for k in MRR_Time.keys()][0:5]
print('\n', 'Ordered top 5 SEs for Time: ', top_5_SE_Time, '\n')

print('\n', 'R Precison Cranfield:')
R_precision_Cranfield = R_precision_function(engines_Cranfield, top_5_SE_Cranfield, GT_Cranfield)
print('\n', 'R Precison Time:')
R_precision_Time = R_precision_function(engines_Time, top_5_SE_Time, GT_time)

PaK_Cranfield = PaK_function([1,3,5,10], engines_Cranfield, top_5_SE_Cranfield, GT_Cranfield)
print('\n','mean_P@K_Cranfield_plot: ','\n')
plot_function(top_5_SE_Cranfield, PaK_Cranfield, 'mean_P@K_Cranfield')
PaK_Time = PaK_function([1,3,5,10], engines_Time, top_5_SE_Time, GT_time)
print('\n','mean_P@K_Time_plot: ','\n')
plot_function(top_5_SE_Time, PaK_Time, 'mean_P@K_Time')

nDCG_Cranfield = nDCG_function([1,3,5,10], top_5_SE_Cranfield, engines_Cranfield, GT_Cranfield)
print('\n','mean_nDCG_Cranfield_plot: ','\n')
plot_function(top_5_SE_Cranfield, nDCG_Cranfield, 'mean_nDCG_Cranfield')
nDCG_Time = nDCG_function([1,3,5,10], top_5_SE_Time, engines_Time, GT_time)
print('\n','mean_nDCG_Time_plot: ','\n')
plot_function(top_5_SE_Time, nDCG_Time, 'mean_nDCG_Time')

print("TimeStamp: ", time.asctime(time.localtime(time.time())))
end = round(time.time(),1)
print('total time: '+str(round((end-start)/60,))+' minutes')

