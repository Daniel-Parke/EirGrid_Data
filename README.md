# Python-Files
## General use guidelines:
This program was enabled to download all data available on the Eirgrid server that is presented on the Eirgrid Smart Dashboard (**https://www.smartgriddashboard.com/#all/demand**). This information encompasses all grid variables recorded by the Network operator within the iSEM for both Northern Ireland, and the Republic of Ireland.

### How to run.
To download the data simply run the python file titled **"async_eirgrid_datadownload.py file"** on the command line. This will generate and save a CSV file with the historical Eirgrid SEMO energy grid data into the downloaded folder. This will be done for each category and region set as variables within the .py file.

### More information.

There are a few basic requirements before running the program to ensure it works correctly. If you are not using an IDE like Jupyter or VScode, then remember to install python 3.9 or higher first before running the .py file. Simply run the .py file in your terminal to start the process, assuming you meet the requirements listed at the bottom. 

There are three .py files that can be run to download the Eirgrid data. The python file "async_eirgrid_datadownload.py" is the current main method I use myself. "parrallel_async_eirgrid_datadownload.py" was a test to see if parrallel processing would improve processing time but it made little difference. The "eirgrid_datadownload.py" file was the first implementation of this program and has the same functionality, but is a lot slower to download all the data as it processes each API call consecutively.

Most datasets contain information from 1st January 2014 onwards, however SNSP data is only available from after 2022 as it was not recorded before this. The time series format for the data ranges from 5 seconds to 30 minutes depending on the dataset obtained, however most use a 15 minute format. More information on the data categories and formats can be found at **"https://www.smartgriddashboard.com/#all"**

The current program will download all data from the earliest range possible up until the end of 2023. To increase the date range to account for future dates, you only need to change the variable "**final_year**" within the "**get_historic_data()**" function. The default value for this is "**24**" which runs the program until the end of 2023. Simply increase this value by one for every additional year after 2023 that you would like to gather data for. Alternatively decrease these values if you would like less data.

The **SNSP** data is **NOT** broken down into regions either, and is only available on an all island basis. This program will generate **Snsp.csv** files for "NI" and "ROI", however these will not be populated with any data and should be ignored. The original dataset included in this repo has had these files deleted from the "NI" and "ROI" folders already.

A copy of the datasets the .py file will collect can be found within the **"Downloaded_Data"**, and includes data from 2014-2023. Due to the size of all frequency data combined being over 3.5GB, a copy of the "frequency" data is **NOT** available in the git hub repo. If you would like a copy of this for the time period 2014-2023 please get in touch.

For the standard program please be aware that if you are downloading all of the datasets (excluding frequency), the script can take up to **30 minutes** to complete due to the extremely large size of the dataset. This time drops to around **11 minutes** if you use the async version of the program. This will further drop to **2.21 minutes** if using the parallel version.

For the frequency data please be aware that the interval for each datapoint is 5 seconds, which equates to over **130,000,000** data points for the entire record. The other datasets only contain time series data with 15 minute intervals, and as a result are much smaller CSV files that can be included.

If the **"frequency"** dataset is not required, then simply delete "frequency" from the category list within the **.py** file to remove it from the function. Currently the frequency category is commented out to help prevent long runtimes, and as such the default operation will not collect it. If frequency data needs to be collected simply delete the **"##"** and make sure the indention is correct before running the **.py** file. 

A copy of the frequency data can also be provided, please get in touch if you would like this.


### Requirements.
Make sure that the packages listed at the bottom of the page are installed on your system, and import using the provided code below.

## Install through command line interface:
    pip install pandas
    pip install requests
    pip install httpx
    pip install httpx[http2]
    pip install backoff
    pip install aiofiles
    
## Libraries used within the Eirgrid data downloader:
    from timeit import default_timer as timer
    import os.path
    import os
    import asyncio
    import requests
    import httpx
    from backoff import on_exception, expo, HTTPStatusError
    from tqdm.asyncio import tqdm
    import pandas as pd
