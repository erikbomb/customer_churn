import pandas as pd
import numpy as np

#Need to add realism to this for customers growing over time, percentage of customers that are more likely to order again etc...

def random_sheet(name):
    #make a quick random date selector
    dates= []
    for i in range(0,365*5):
        dates.append(np.datetime64('2016-01-01') + i)
    
    # setting the number of rows for the CSV file
    N = 1000000
    # make the table outline with random numbers
    df = pd.DataFrame(np.random.randint(999,999999,size=(N, 4)), columns=["CustomerNumber","PurchaseDate","TotalItems","InvoiceTotal"])
    # randomize the purchase date, totalItems, Invoice total
    df["PurchaseDate"] = np.random.choice(dates, N)
    df["TotalItems"] = np.random.randint(1,100, N)
    df["InvoiceTotal"] = np.random.uniform(1.00,10000.00,N)
    df["InvoiceTotal"] = np.round(df["InvoiceTotal"],decimals= 2)
    # print the dataframe to see what we have created
    print(df)
    # export the dataframe to csv using comma delimiting
    df.to_csv('random'+name+'.csv', sep=",")

num_sheets=5
for i in range(0,num_sheets):
    random_sheet(str(i))
