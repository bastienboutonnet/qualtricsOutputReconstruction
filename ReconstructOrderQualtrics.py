
# coding: utf-8

## Reconstruct Order & Qualtrics Output

# **Author**: Bastien Boutonnet (with help from bits of code from Pierce. Thank!)
# 
# When you use Loop and merge in Qualtrics and are interested in knowing when participants saw what item out of the loop and merge, it can be a little tricky.
# 
# Here's a walthrough on how to recreate and merge with your data the trial order using the output of the "preorder" javascript code which (if implemented in your survey) spits out a string containing the order of your stimuli/trial.

## Load data files

# In[83]:

import pandas as pd
import numpy as np

df=pd.read_csv("dummyData.csv") #you may wanna add skiprows=[1,] if opening a qualtrics file which has a shitty header.
# df=df.rename(columns={df.columns[0]:'subj_id'}) #again you'd do that if opening a raw qualtrics output.


# In[84]:

df


# In[85]:

loopmergeInfo=pd.read_csv("dummyLoopmerge.csv") #a file containing row and Names corresponding to your loop&Merge


# In[86]:

loopmergeInfo


# For convenience we want to create a df that contains the subject info (important for merging later)
# and the output from the js script which lists the order of the trials.

# In[87]:

#pull out subject id and preorder column from raw file to work on it.
#That is assuming the js you have in qualtrics spits out a column called "order" modify name to fit your needs.
ord=df[['subj_id','order']] 


## Parse Out the order

# 1. Let's make a list of the variables for which to parse the order.
# 
# You can either write them manually or simply pull them out from your loopmergeInfo file and put then in an array.

# In[88]:

variables=loopmergeInfo.Name.as_matrix()
variables


# 2. Split the strings that the js script created into an array

# In[89]:

order_split=ord.order.str.split("|")

print order_split
print "beautiful!" #for shits and giggles!


# 3. Let the magic happen:
# 
# Looping over the list of variables we created earlier, we will create a column for each of those, and fill in the index (location) of each variables. We add 1 because python is odd and likes to index from 0... (MATLAB/R user complaint).

# In[90]:

for v in variables:
        ord[v] = order_split.apply(lambda x: x.index(v) + 1)

ord


# This is starting to look sexy. We now essentially have our order reconstructed. Next!
# 
# 4. Melt to long format (because the longer the better...)

# In[91]:

#actually let's do a bit of housekeeping first
#by dropping the now redundant "order" column. Bye Felicia!
order=ord.drop(['order'],axis=1) 
#don't forget axis=1 it tells to do the drop on the column dimention
#0 would tell it to do this for row. 

#then melt!
#At this point it's up to you what you name your variable,
#but keep it the same as the column your loopmerge info has since you'll want to
#use that column to merge the order and data together later.
order=pd.melt(order,id_vars='subj_id',var_name='Name',value_name='position')

print "BOOM!"
order


# At this point you can see how this is already looking very close to the output you'd have reconstructed from qualtrics. Let's go through this now!

## Reconstruc Qualtrics Output

### Column Selection (aka. "clean after Qualtics")

# In[92]:

col_names=pd.Series(df.columns) # convert to pandas.Series to use str methods

#create a mask to retain what you want
#this uses regular expressions, this one says:
#from begining of string take stuff that matches "subj_id" or "Q"
valid_cols_mask=col_names.str.contains('^subj_id|Q',regex=True) 

#This returns bolean values: True for "keep column" false... you know what for.
valid_cols_mask


# In[93]:

#now we can apply that mask and get rid of what we don't want
valid_cols = df.columns[valid_cols_mask]
valid_cols


# In[94]:

#and then we want to actually update our df and subset/select those columns we kept
df=df[valid_cols]
print "bye column 5!"
df


## Melt Qualtrics Output

# In[95]:

#Right let's melt this (reason given above!)
df=pd.melt(df,id_vars='subj_id',var_name='qual_col',value_name='RT')
df


## Make some damn sense! (Almost there!) 

# In[96]:

#Lets split the info from the qualtrics arcane naming system
#RegEx again. This one, a bit more tricky: (can be modified to suit your needs)
#1. Take anything that is a string (\w stands for "word character", usually [A-Za-z0-9_]) 
#stop at"(" put this in a column called "measure"
#2. Take anything that's a number (d+), stop when you see ")"
#and put this in a column called "row"
#NOTE. you want that column to be the same as in your loopmerge info
qualtrics_parsed=df.qual_col.str.extract('^(?P<measure>\w+)\((?P<row>\d+)\)$')
qualtrics_parsed = qualtrics_parsed.convert_objects(convert_numeric=True) #you want numbers to be integers
print "BAAM!"
qualtrics_parsed


# In[97]:

#put the two together, simple concat based on row index here.
df = pd.concat([df, qualtrics_parsed], axis = 1)
df


## Really make some sense...

# In[98]:

#you want to merge your newly created df
#it is now ready to be bind to the info from loopmerge
df = df.merge(loopmergeInfo, how='left') #assuming both df and loopmergeInfo have a "row" col.
#By the magic of merge it gives you this
print "BIIM, BAAM, BOOM!"
df


## Merge Data and Order

# In[99]:

#All we have do to now is merge the order we created, with the real
#data. 
datNorder=pd.merge(df,order,how='left',on=['Name','subj_id'])


## THE MONEY SHOT!

# In[100]:

datNorder


## THE SANITY CHECK

# In[101]:

a=ord[['subj_id','order']]
b=datNorder[['subj_id','Name','position']]
print a
b


## Cleaning Lady time!

# In[102]:

datNorder = datNorder.drop(['qual_col', 'row','measure'], axis=1) # drop redundant or uninformative columns
#keep "row" if you're planning on adding other DVs, as it'll be usefully
datNorder =datNorder[['subj_id', 'Name', 'position','RT']] # arrange columns
datNorder = datNorder.sort(['subj_id','Name']) # you can sort it too!
datNorder = datNorder.reset_index(drop=True) # reset the index (just because, Pierce said so!)
datNorder


# In[ ]:



