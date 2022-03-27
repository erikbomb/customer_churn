import pandas as pd
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from datetime import datetime
from tqdm import tqdm
import time
import argparse


#name of columns that I need
purchase_date='PurchaseDate'
customer_number="CustomerNumber"
total_items="TotalItems"
invoice_total="InvoiceTotal"

        
# Borrowed to display time it takes to run the program
intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def print_message(message, message_type=0, location=0):
    # todo: setup logging with python log
    # 0 - regular, 1 - warning, 2 - missing
    types= ["[ ] - ","[!] - ","      "]
    # location 0 - console , 1 - logs, 2 - both
    print(types[message_type] + message)

def get_files():
    # quick gui file selector
    Tk().withdraw()
    return askopenfilename()


def calculate(df):
    #fix the data
    print_message("Convertings dates to date_time",0,0)
    df[purchase_date]  = pd.to_datetime(df[purchase_date], format='%Y-%m-%d')
    print_message("dates converted",0,0)
    #get the number of months to iterate through
    start_date=pd.to_datetime(min(df[purchase_date]))
    end_date=pd.to_datetime(max(df[purchase_date]))
    # had to add 1 to make sure that it includes both months
    number_of_months=np.int(np.floor(((end_date - start_date)/np.timedelta64(1,'M'))))+1
    column_names = ["month","returning_customers","lost_customers","gained_customers","total_customers"]
    churn_data = pd.DataFrame(columns = column_names)
    #go through monthly and figure out the stuff...
    new_row = {'month':"", 'returning_customers':0,'gained_customers':0,'lost_customers':0,'total_customers':0}
    for month in range(0,number_of_months + 1):
        print_message("Starting month number " +str(month),0,0)
        # set the start and end of a month
        previous_month_start =pd.to_datetime(start_date + pd.DateOffset(months=month-1))
        current_month_start =pd.to_datetime(start_date + pd.DateOffset(months=month))
        next_month_start =pd.to_datetime(start_date + pd.DateOffset(months=month+1))
        print("Previous month start: " + str(previous_month_start))
        print("Current month start: " + str(current_month_start))
        print("Next month start: " + str(next_month_start))
        #only look at customers that purchase last month or this month
        unique_customers=df.loc[(df[purchase_date] >= previous_month_start) & (df[purchase_date] < next_month_start)][customer_number].unique().tolist()
        #add the new month to the df
        new_row = {'month':current_month_start, 'returning_customers':0,'gained_customers':0,'lost_customers':0,'total_customers':new_row['total_customers']}
        for customer in tqdm(unique_customers):
            check_customer(customer,new_row,df,previous_month_start,current_month_start,next_month_start)
        new_row['total_customers']=new_row['total_customers'] + new_row["gained_customers"]
        churn_data = churn_data.append(new_row, ignore_index=True)
        print (churn_data.iloc[-1])
    return churn_data

def check_customer(customer,new_row,df,previous_month_start,current_month_start,next_month_start):
    #get current customer 
    customer_data = df.loc[df[customer_number] == customer]
    #check for any purchases and record for this month
    purchase_this = customer_data.loc[(customer_data[purchase_date] >= current_month_start) & (customer_data[purchase_date] < next_month_start)]
    purchase_this_month = not purchase_this.empty
    #check for any purchases and record before this month
    purchase_prior = customer_data.loc[(customer_data[purchase_date] < current_month_start)]
    purchase_prior_month = not purchase_prior.empty
    #check for any purchases and record after this month
    purchase_future = customer_data.loc[(customer_data[purchase_date] >= next_month_start)]
    purchase_future_month = not purchase_future.empty
    #set the values in the dataframe
    if purchase_prior_month:
        if purchase_this_month:
            new_row["returning_customers"] = new_row["returning_customers"] + 1
        elif not purchase_future_month:
            new_row["lost_customers"] = new_row["lost_customers"] + 1
    elif purchase_this_month:
        new_row["gained_customers"] = new_row["gained_customers"] + 1

def setup(args):
    # allow user to keep getting files
    filename = "blank"
    files_list = []
    if args['test']:
        files_list.append('data/random1.csv') 
    else:
        # keep going and add files to array if it is not a blank file
        while filename:
            filename=get_files()
            if filename:
                files_list.append(filename)
    #load in the data 
    print_message("loading the following files:",0,1) 
    frames = [] 
    for i in files_list: 
        print_message(i,2,1) 
        frames.append(pd.read_csv(i)) 
    return pd.concat(frames)

def run(args):
    df = setup(args)
    #how much memory are we using?
    df.info(memory_usage="deep")
    excel=calculate(df)
    excel.to_csv('customer_churn.csv', sep=",")

#dirty start, reorganize for better code
parser = argparse.ArgumentParser(description='Customer Chrun rate')
parser.add_argument('-t','--test', help='test case instead of manual file selection', action='store_true')
args = vars(parser.parse_args())
# get the start time and then run, finish with total time
start_time = time.time()
run(args)
x=display_time(time.time() -start_time,5)
# we are done - show the time in calculation
print ("time: "+ x)
