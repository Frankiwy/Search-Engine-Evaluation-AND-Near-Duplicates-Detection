
# coding: utf-8


import csv
from collections import defaultdict
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


def NDD_function(path):
    '''
    The function is used to import Near Duplicates:
    :param path: # the path where the APPX_NDD .tsv file is stored
    :return: the near duplicates dictonary where the key is approx. Jaccard similarity and the value the total number of couples retrieved with that approx. Jaccard
    '''

    NDD =defaultdict(list)  # dict where the counted real duplicates will be reported
    with open(path) as tsvfile:
        tsvreader = csv.reader(tsvfile, delimiter='\t')
        next(tsvreader)
        for line in tsvreader:
            NDD[round(float(line[0]), 2)].append(1) # take approx. Jaccard value and add 1 into its list

    NDD.update((x, sum(y)) for x, y in NDD.items())  # sum up all the 1 in the lists (this is performed in order to know how many couples are in every approx. Jaccard similarity value )
    NDD = {k: v for k, v in sorted(NDD.items(), key=lambda item: item[0], reverse=False)}  # sort by key
    NDD = {k: sum(list(NDD.values())[e:]) for e, (k, v) in enumerate(NDD.items())}  # perform the commulative (this is perfomed in order to answer to the last point of the task)
    df = df = pd.DataFrame(list(NDD.items()), columns=['Jaccard', 'At least Jaccard']) # store the commulative values and the Approx. Jaccard similarity into pandas df (this is done, in order to plot)

    return (NDD, df)  # return the dict and the df

def BarPlot_plot(df):
    fig = plt.figure(figsize=(30, 15))
    ax = sns.barplot(x="Jaccard", y='At least Jaccard', palette="GnBu_d", data=df)
    
    ax.set(ylabel='n° of Near Duplicates couples', xlabel='At least Approx. Jaccard Similarity')
    ax.set_xticklabels(labels=df["Jaccard"], fontsize=20, rotation=80)
    ax.xaxis.labelpad = 15
    ax.yaxis.labelpad = 15
    ax.xaxis.label.set_size(35)
    ax.yaxis.label.set_size(35)
    ax.xaxis.label.set_color('red')
    ax.yaxis.label.set_color('red')
    ax.tick_params(axis='both', labelsize=30)

    # here we iterate in order to add the values on top of the bars in the bar plot
    for e, p in enumerate(ax.patches):
        percentage = str(df['At least Jaccard'][e]) # pick the value
        x = p.get_x() + 0.15  # get x coordinate
        y = p.get_y() + p.get_height() + 300  # get y coordinate
        ax.annotate(percentage, (x, y), fontsize=25, color='k')
    
    plt.style.use('Solarize_Light2')
dict_10_10, df_10_10 = NDD_function("./dataset/APPX_NDD__lyric_datasets_for_LSH__10_10.tsv")
BarPlot_plot(df_10_10)

