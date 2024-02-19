# Runtime of program without collecting frequency data was  1833.58 seconds / 30.56 minutes.
from timeit import default_timer as timer
import os
import requests
import pandas as pd
import logging
from datetime import datetime

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)  # Suppress detailed logs from 'requests' library

# Start Timer.
start = timer()

def main():
    """Main structure calling requested functions from below."""
    regions = ["ALL", "ROI", "NI"]
    for region in regions:
        get_historic_data(region)

    # End Timer and calculate runtime.
    end = timer()
    total_time = end - start
    logging.info(f"This script took approx. {round(total_time, 2)} seconds to complete.")
    logging.info("********************************************************")


def get_historic_data(region="ALL"):
    """Main function setting up API and collecting data."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    categories = [
        "demandactual",
        "generationactual",
        "windactual",
        "interconnection",
        "co2intensity",
        "co2emission",
        "SnspALL",
        ## "frequency",
    ]

    final_year = datetime.now().year-1999
    for category in categories:
        year_range = (21, final_year) if category == "SnspALL" else (14, final_year)
        for year in range(*year_range):
            frames = []
            for month_idx, month in enumerate(months):
                next_month = "Jan" if month_idx == 11 else months[month_idx + 1]
                next_year = year + 1 if month_idx == 11 else year
                api = (
                    f"https://www.smartgriddashboard.com/DashboardService.svc/data?area"
                    f"={category}&region={region}&datefrom=01-{month}-20{year}"
                    f"+00%3A00&dateto=01-{next_month}-20{next_year}+21%3A59"
                )
                
                try:
                    response = requests.get(api, timeout=60).json()
                    result = response["Rows"]
                    frames.append(pd.DataFrame(result))
                    logging.info(f"Download of {region} {month} {year} Eirgrid {category.title()} Data was successful.")
                except Exception as e:
                    logging.error(f"Failed to download data for {region} {month} {year} {category.title()}: {e}")

            if frames:
                final_df = pd.concat(frames)
                csv_dir = os.path.join("Downloaded_Data", region)
                os.makedirs(csv_dir, exist_ok=True)
                csv_file = os.path.join(csv_dir, f"{region}_{category.title()}_{year}_Eirgrid.csv")
                final_df.to_csv(csv_file, index=False, header=False)
                logging.info(f"CSV for {region} {year} Eirgrid {category.title()} Data save was successful.")

if __name__ == "__main__":
    main()
