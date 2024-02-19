# Eirgrid Data Downloader

## General Use Guidelines
This script is designed to download all available data on the Eirgrid server presented on the [Eirgrid Smart Dashboard](https://www.smartgriddashboard.com/#all/demand). This information encompasses all grid variables recorded by the Network operator within the iSEM for both Northern Ireland and the Republic of Ireland. Either run the .exe or .py file to execute the script.

### How to Run
To download the data, simply run the exe file titled **"async_eirgrid_datadownload.exe"**, this .exe file can be found in the releases section on the github repository homepage. This will generate and save a CSV file with the historical Eirgrid iSEM grid data into a folder title `Downloaded_Data` in the same location the file is run from. 

This .exe file was compiled directly from the **"async_eirgrid_datadownload.py"** if you would like to see the specific functionality before running the program. I personally do not recommend downloading and running .exe files from sources you cannot verify yourself, but I have added the option to make life easier for those that may come to trust the projects I work on. Any questions regarding how the script operates don't hesitate to reach out.

### More Information
Before running the program, ensure you meet the basic requirements to ensure its correct execution. If you are not using an IDE like Jupyter or VSCode, then remember to install Python 3.9 or higher first. Run the .py file in your terminal to start the process, assuming you meet the requirements listed below.

There are two .py files that can be run directly to download the Eirgrid data instead of the .exe file:
- **async_eirgrid_datadownload.py**: The primary script for data download.
- **eirgrid_datadownload.py**: The initial implementation, slower due to sequential API calls.

Most datasets contain information from January 1, 2014, onwards. However, SNSP data is only available after 2022 as it was not recorded before this. The time series format for the data ranges from 5 seconds to 30 minutes depending on the dataset obtained, however, most use a 15-minute format. More information on the data categories and formats can be found on the [Eirgrid Smart Dashboard](https://www.smartgriddashboard.com/#all).

### Data Categories available:
- **"demandactual"**: Energy demand at timestamp
- **"generationactual"**: Energy generation at timestamp
- **"windactual"**: Wind energy generation at timestamp
- **"interconnection"**: Energy supplied through grid interconnectors
- **"co2intensity"**: Grid CO2 intensity of energy consumed at timestamp
- **"co2emission"**: Total CO2 emissions produced by grid at timestamp
- **"SnspALL"**: System Non-Synchronous Penetration at timestamp
- **"frequency"**: Frequency of electrical grid measured at timestamp

### Regions Data Includes
- **"NI"**: Northern Ireland
- **"NI"**: Replublic of Ireland
- **"ALL"**: All island combined values

The current program will download all data from the earliest range possible up until the end of the current year. To adjust the date range, simply change the variable **current_year** within the **get_historic_data()** function. The default value for this is the current year + 1, which runs the program until the end of the current year.

Note that **SNSP** data is **NOT** broken down into regions and is only available on an all-island basis. This program will generate **Snsp.csv** files for "NI" and "ROI"; however, these will not be populated with data and should be ignored. The original dataset included in this repo has had these files deleted from the "NI" and "ROI" folders already.

A copy of the datasets the .py file will collect can be found within the **"Downloaded_Data"** folder, which includes data from 2014-2023. Due to the size, a copy of the "frequency" data is **NOT** available in the GitHub repo. If you would like a copy of this for the period 2014-2023, please get in touch. If you would like to include frequency data in your download function, then simply add this to the categories defined in the function using the string naming convention shown below **("frequency")**. 

Both .py file implementations define a list of categories before running the function calls, it is that category list you need to add "frequency" to. I recommend adding this to the end of the list so that all other datasets will be downloaded and saved first.

Downloading all datasets (excluding frequency) can take up to **30 minutes** due to the large size of the dataset. Using the async version of the program reduces this time to around **11 minutes**, with the parallel version reducing times even further depending on your system.


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

![WiseWattage](https://i.imgur.com/Y7oMz2Y.png)
