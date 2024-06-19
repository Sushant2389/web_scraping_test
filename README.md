# web_scraping_test

# Web Scraping Project

Url(case1):  https://nevadaepro.com/bso/view/search/external/advancedSearchBid.xhtml?openBids=true
url(case2)  : https://isd110.org/our-schools/laketown-elementary/staff-directory


## Setup

1. Clone the repository:
  
    >>>git clone https://github.com/Sushant2389/web_scraping_test.git


2. Create a virtual environment and activate it:
  
    >>>python -m venv venv
    >>>source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    

3. Install the dependencies:

  Please download requirements.txt file from code folder and install all the pacakges in virtual environment as follow:

    >>>pip install -r requirements.txt
  

## Running the Script

#Run the script using:

>>>python case1.py for problem statement-1


>>> python case2.py for problem statement-2

## output structure:

Each script will generate output and store it in the respective folders:

1. case1.py: The output is stored in the case1_output folder. This includes a JSON file containing bid details and subfolders with downloaded attachments.
2. case2.py: The output is stored in the case2_output folder, where the processed data is saved as a CSV file.

## Logs
1. Logs are generated during script execution to help with debugging and tracking progress. 
2. All log files are stored in the code/logs folder. 
3. Each script has its own log file named in the format scriptname_log.txt.


## Observations:
Case1:

1. There are a total of 17 entries for bids, but only 16 of them are available in the DOM. One possible reason for this discrepancy might be that the due date for some bids has passed, as indicated by the message "Due date has passed. Vendors can no longer submit quotes" on the inner page of certain bids.

2. The script ensures that it does not reprocess bids already encountered in previous pages, thereby avoiding duplicate entries and redundant processing