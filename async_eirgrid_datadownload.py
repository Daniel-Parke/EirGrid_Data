# Runtime of program without collecting frequency data was 672.29 seconds / 11.2 minutes.
from timeit import default_timer as timer
import asyncio
import os
import logging
from backoff import on_exception, expo
import httpx
import pandas as pd
from httpx import HTTPStatusError
from tqdm.asyncio import tqdm
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("httpx").setLevel(logging.WARNING)

# Timer start
start = timer()

async def main():
    async with httpx.AsyncClient(http2=True) as client:
        semaphore = asyncio.Semaphore(10)
        regions = ["ALL", "ROI", "NI"]
        tasks = [get_historic_data(client, region, semaphore) for region in regions]
        await asyncio.gather(*tasks)

@on_exception(expo, HTTPStatusError, max_tries=8)
async def fetch_data(client, api, timeout=25):
    try:
        response = await client.get(api, timeout=timeout)
        response.raise_for_status()
        return response.json()["Rows"]
    except HTTPStatusError as e:
        logging.error(f"HTTPStatusError for API {api}: {e}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error for API {api}: {e}")
        raise

async def get_historic_data(client, region="ALL", semaphore: asyncio.Semaphore = None):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    categories = ["demandactual", "generationactual", "windactual", "interconnection", "co2intensity", "co2emission", "SnspALL"]
    final_year = datetime.now().year-1999
    for category in tqdm(categories, desc=f"Fetching categories for {region}"):
        year_range = (21, final_year) if category == "SnspALL" else (14, final_year)
        for year in range(*year_range):
            frames = []
            # Use tqdm to track progress for each month
            async for month in tqdm(months, desc=f"Fetching data for {category} - Year: {year}", leave=False):
                month_idx = months.index(month)
                next_month = months[0] if month_idx == 11 else months[month_idx + 1]
                next_year = year + 1 if month_idx == 11 else year
                api = (
                    f"https://www.smartgriddashboard.com/DashboardService.svc/data?"
                    f"area={category}&region={region}&"
                    f"datefrom=01-{month}-20{year}+00%3A00&"
                    f"dateto=01-{next_month}-20{next_year}+21%3A59"
                )
                async with semaphore:
                    try:
                        data = await fetch_data(client, api)
                        frames.append(pd.DataFrame(data))
                    except Exception as e:
                        logging.warning(f"Failed to fetch or process data for {api}: {e}")
                        continue
            if frames:
                final_df = pd.concat(frames)
                csv_dir = f"Downloaded_Data/{region}"
                os.makedirs(csv_dir, exist_ok=True)
                csv_file = f"{csv_dir}/{region}_{category}_{year}_Eirgrid.csv"  # Adjusted to use year instead of month_idx for filename
                final_df.to_csv(csv_file, index=False, header=False)
                logging.info(f"File saved: {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())
    end = timer()
    logging.info("********************************************************")
    logging.info(f"Script completed in {round(end - start, 2)} seconds.")
    logging.info("********************************************************")
