# Runtime of program without collecting frequency data was  1833.58 seconds / 30.56 minutes.
""" Import functions and libraries required for functionality. """
from timeit import default_timer as timer
import os.path
import requests
import pandas as pd

# Start Timer.
start = timer()


def main():
    """Main structure calling requested functions from below."""
    get_historic_data("ALL")
    get_historic_data("ROI")
    get_historic_data("NI")

    # End Timer and calculate runtime.
    end = timer()
    total_time = end - start
    print("")
    print(f"This script took approx. {round(total_time, 2)} seconds to complete.")
    print("********************************************************")
    print("")


def get_historic_data(region="ALL"):
    """Main function setting up API and collecting data"""
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
        ## "frequency",
    ]

    initial_year = 14
    final_year = 24
    year = 14

    # Loop through each category to perform each action.
    for catx, category in enumerate(category):  # pylint: disable=unused-variable
        if category == "SnspALL":
            initial_year, year = 21, 21

        else:
            initial_year, year = 14, 14

        # Iterate through each year and add collected data to dataframe.
        for i in range(final_year - initial_year):
            frames = []

            # Iterate through each month and edit API accordingly. Pull data and add to list of dataframes.             # pylint: disable=line-too-long
            for j in range(12):
                if j == 11:
                    api = (
                        f"https://www.smartgriddashboard.com/DashboardService.svc/data?area"
                        f"={category}&region={region}&datefrom=01-{month[j]}-20{year + i}"
                        f"+00%3A00&dateto=01-{month[0]}-20{year + i + 1}+21%3A59"
                    )
                    date = f"{month[j]} {year + i}"

                else:
                    api = (
                        f"https://www.smartgriddashboard.com/DashboardService.svc/data?area"
                        f"={category}&region={region}&datefrom=01-{month[j]}-20{year + i}"
                        f"+00%3A00&dateto=01-{month[j + 1]}-20{year + i}+21%3A59"
                    )
                    date = f"{month[j]} {year + i}"

                # Access data API and save data in json format.
                req = requests.get(api, timeout=60)

                response = req.json()

                # Store the key values under "Rows" in json data, ignoring the other key pairs, and save to dataframe.
                result = response["Rows"]
                datafr = pd.DataFrame(result)
                frames.append(datafr)

                # Confirm action completed.
                print(
                    f"{i+1}.{j+1} - Download of {region}_{date} Eirgrid {category.title()} Data was successful."
                )

            # Merge dataframe lists and save data to CSV file.
            final = pd.concat(frames)

            # Ensure the directory exists
            csv_dir = os.path.join("Downloaded_Data", region)
            os.makedirs(csv_dir, exist_ok=True)  # Create directory if it does not exist

            final.to_csv(
                os.path.join(
                    f"Downloaded_Data/{region}",
                    (f"{region}_{category.title()}_{date}_Eirgrid.csv"),
                ),
                index=False,
                header=False,
            )

            # Confirm action completed.
            print(
                f"CSV for {region} {date} Eirgrid {category.title()} Data save was successful."
            )

            print("")


if __name__ == "__main__":
    main()


## Eirgird api - https://www.smartgriddashboard.com/DashboardService.svc/data?area=co2intensity&region=ALL&datefrom=01-Jan-2014+00%3A00&dateto=01-Feb-2014+21%3A59
