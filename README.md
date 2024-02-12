# Eirgrid Data Downloader

## General Use Guidelines
This script is designed to download all available data on the Eirgrid server presented on the [Eirgrid Smart Dashboard](https://www.smartgriddashboard.com/#all/demand). This information encompasses all grid variables recorded by the Network operator within the iSEM for both Northern Ireland and the Republic of Ireland.

### How to Run
To download the data, simply run the python file titled **"async_eirgrid_datadownload.py"** on the command line. This will generate and save a CSV file with the historical Eirgrid SEMO energy grid data into the downloaded folder. This process is repeated for each category and region set as variables within the .py file.

### More Information
Before running the program, ensure you meet the basic requirements to ensure its correct execution. If you are not using an IDE like Jupyter or VSCode, then remember to install Python 3.9 or higher first. Run the .py file in your terminal to start the process, assuming you meet the requirements listed below.

There are three .py files that can be run to download the Eirgrid data:
- **async_eirgrid_datadownload.py**: The primary script for data download.
- **parallel_async_eirgrid_datadownload.py**: A test for parallel processing with minimal impact on performance.
- **eirgrid_datadownload.py**: The initial implementation, slower due to sequential API calls.

Most datasets contain information from January 1, 2014, onwards. However, SNSP data is only available after 2022 as it was not recorded before this. The time series format for the data ranges from 5 seconds to 30 minutes depending on the dataset obtained, however, most use a 15-minute format. More information on the data categories and formats can be found on the [Eirgrid Smart Dashboard](https://www.smartgriddashboard.com/#all).

The current program will download all data from the earliest range possible up until the end of 2023. To adjust the date range for future dates, simply change the variable **final_year** within the **get_historic_data()** function. The default value for this is **24**, which runs the program until the end of 2023. Increase this value by one for each additional year you wish to gather data for, or decrease it for less data.

Note that **SNSP** data is **NOT** broken down into regions and is only available on an all-island basis. This program will generate **Snsp.csv** files for "NI" and "ROI"; however, these will not be populated with data and should be ignored. The original dataset included in this repo has had these files deleted from the "NI" and "ROI" folders already.

A copy of the datasets the .py file will collect can be found within the **"Downloaded_Data"** folder, including data from 2014-2023. Due to the size, a copy of the "frequency" data is **NOT** available in the GitHub repo. If you would like a copy of this for the period 2014-2023, please get in touch. If you would like to include frequency data in your download function, then simply add this to the categories defined in the function using the string naming convention shown below **("frequency")**.

Downloading all datasets (excluding frequency) can take up to **30 minutes** due to the large size of the dataset. Using the async version of the program reduces this time to around **11 minutes**, with the parallel version reducing times even further depending on your system.


### Data Categories available:
- **"demandactual"**: Energy demand at timestamp
- **"generationactual"**: Energy generation at timestamp
- **"windactual"**: Wind energy generation at timestamp
- **"interconnection"**: Energy supplied through grid interconnectors
- **"co2intensity"**: Grid CO2 intensity of energy consumed at timestamp
- **"co2emission"**: Total CO2 emissions produced by grid at timestamp
- **"SnspALL"**: System Non-Synchronous Penetration at timestamp
- **"frequency"**: Frequency of electrical grid measured at timestamp

### Requirements
Ensure the following packages are installed on your system:

- pandas
- requests
- httpx
- backoff
- aiofiles

**Install through command line interface:**
```python
pip install pandas
pip install requests
pip install httpx
pip install httpx[http2]
pip install backoff
pip install aiofiles
```
    
**Libraries used within the Eirgrid data downloader:**
```python
from timeit import default_timer as timer
import os.path
import os
import asyncio
import requests
import httpx
from backoff import on_exception, expo, HTTPStatusError
from tqdm.asyncio import tqdm
import pandas as pd
```

