# Runtime of program without collecting frequency data was  732.84 seconds / 12.21 minutes.
from timeit import default_timer as timer
import asyncio
import os
from backoff import on_exception, expo
import httpx
import pandas as pd
from httpx import HTTPStatusError
from tqdm.asyncio import tqdm

# Timer start
start = timer()

# A decorator-based exponential backoff retry mechanism for asynchronous calls
@on_exception(expo, HTTPStatusError, max_tries=8)
async def fetch_data(client, api):
    response = await client.get(api)
    response.raise_for_status()
    return response.json()["Rows"]

async def get_historic_data(client, region="ALL", semaphore: asyncio.Semaphore = None):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    categories = ["demandactual", "generationactual", "windactual", "interconnection", "co2intensity", "co2emission", "SnspALL"]
    
    async for category in tqdm(categories, desc=f"Fetching categories for {region}"):
        year_range = (21, 21) if category == "SnspALL" else (14, 24)
        
        for year in range(*year_range):
            frames = []
            
            for month_idx, month in enumerate(tqdm(months, desc=f"Year: {year}", leave=False)):
                next_month = months[0] if month_idx == 11 else months[month_idx + 1]
                next_year = year + 1 if month_idx == 11 else year
                api = (
                    f"https://www.smartgriddashboard.com/DashboardService.svc/data?"
                    f"area={category}&region={region}&"
                    f"datefrom=01-{month}-20{year}+00%3A00&"
                    f"dateto=01-{next_month}-20{next_year}+21%3A59"
                )

                # Access data API and save data in json format. Use semaphore to limit concurrent requests
                async with semaphore:
                    try:
                        data = await fetch_data(client, api)
                    except HTTPStatusError as e:                                                         # pylint: disable=unused-variable
                        continue
                    except Exception as e:                                                               # pylint: disable=broad-exception-caught
                        continue

                    frames.append(pd.DataFrame(data))

            if frames:
                final_df = pd.concat(frames)
                csv_dir = f"Downloaded_Data/{region}"
                os.makedirs(csv_dir, exist_ok=True)
                csv_file = f"{csv_dir}/{region}_{category}_{months[month_idx]}_{year}_Eirgrid.csv"          # pylint: disable=undefined-loop-variable
                final_df.to_csv(csv_file, index=False, header=False)
                tqdm.write(f"File saved: {csv_file}")


async def main():
    async with httpx.AsyncClient(http2=True) as client:
        semaphore = asyncio.Semaphore(10)
        regions = ["ALL", "ROI", "NI"]
        tasks = [get_historic_data(client, region, semaphore) for region in regions]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
    end = timer()
    print("")
    print("********************************************************")
    print(f"\nScript completed in {round(end - start, 2)} seconds.")
    print("********************************************************")
    print("")
