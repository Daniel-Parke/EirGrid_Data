# Runtime of program without collecting frequency data was  752.52 seconds / 12.54 minutes.
from timeit import default_timer as timer
import asyncio
import os
import httpx
import pandas as pd
import backoff

# Timer start
start = timer()

MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
]

def get_next_month(current_month, year):
    """Helper function to get the next month and year."""
    month_index = MONTHS.index(current_month) + 1
    if month_index == 12:  # If December, wrap around to January and increment year
        return "Jan", year + 1
    else:
        return MONTHS[month_index], year

# Backoff and retry strategy
@backoff.on_exception(
    backoff.expo,
    (httpx.HTTPError, httpx.ReadTimeout),
    max_tries=8,
    giveup=lambda e: hasattr(e, "response")
    and e.response is not None
    and e.response.status_code < 500,
)
async def fetch_data(client, category, year, mon, region, semaphore):
    """Fetch data from API with exponential backoff on HTTP errors."""
    date = f"{mon} {year}"
    next_mon, next_year = get_next_month(mon, year)
    
    api = (
        f"https://www.smartgriddashboard.com/DashboardService.svc/data?"
        f"area={category}&region={region}&"
        f"datefrom=01-{mon}-20{year}+00%3A00&"
        f"dateto=01-{next_mon}-20{next_year}+00%3A00"
    )

    async with semaphore:
        response = await client.get(api)
        response.raise_for_status()
        return response.json()["Rows"], date


async def get_historic_data(client, region="ALL", semaphore: asyncio.Semaphore = None):
    """Asynchronous function to set up API and collect data with semaphore and backoff."""
    month = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    category = [
        "demandactual",
        "generationactual",
        "windactual",
        "interconnection",
        "co2intensity",
        "co2emission",
        "SnspALL",
    ]

    for cat_name in category:
        # Adjust the year range for 'SnspALL' category
        year_range = (21, 21) if cat_name == "SnspALL" else (14, 24)

        for year in range(*year_range):
            frames = []
            tasks = []

            for idx, mon in enumerate(month):  # pylint: disable=unused-variable
                # Schedule fetch_data for execution and append task
                task = fetch_data(client, cat_name, year, mon, region, semaphore)
                tasks.append(task)

            # Gather data from all scheduled tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process successful results and handle exceptions
            for result in results:
                if isinstance(result, Exception):
                    print(f"An error occurred: {result}")
                else:
                    data, date = result
                    datafr = pd.DataFrame(data)
                    frames.append(datafr)

            # Save to CSV if there are frames collected
            if frames:
                final_df = pd.concat(frames)
                csv_path = os.path.join(
                    f"Downloaded_Data/{region}",
                    f"{region}_{cat_name.title()}_{date}_Eirgrid.csv",
                )
                os.makedirs(os.path.dirname(csv_path), exist_ok=True)
                final_df.to_csv(csv_path, index=False, header=False)
                print(
                    f"CSV for {region} {date} Eirgrid {cat_name.title()} Data save was successful."
                )
                print("*********************************")


async def main():
    """Asynchronous main structure to call requested functions concurrently with semaphore."""
    async with httpx.AsyncClient(http2=True, timeout=10.0) as client:
        semaphore = asyncio.Semaphore(10)  # Adjust the number as necessary
        tasks = [
            get_historic_data(client, region, semaphore)
            for region in ["ALL", "ROI", "NI"]
        ]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

    # End timer and calculate total time
    end = timer()
    total_time = end - start
    print(
        f"\nThis script took approximately {round(total_time, 2)} seconds to complete."
    )
    print("********************************************************")
