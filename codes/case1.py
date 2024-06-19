import requests
from bs4 import BeautifulSoup
import json
import os
import logging

# Create a 'logs' directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')
    
# Set up logging
log_file = os.path.join('logs', 'case1_log.txt')
os.makedirs(os.path.dirname(log_file), exist_ok=True)  
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)


base_url = "https://nevadaepro.com"
search_url = f"{base_url}/bso/view/search/external/advancedSearchBid.xhtml?openBids=true"

def get_soup(url):
    try:
        """Fetch the content of the given URL and return a BeautifulSoup object."""
        response = requests.get(url)
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        logging.error(f"An error occurred in function => get_soup: {str(e)}")
        
def extract_bid_data(soup):
    """Extract bid data from the search results page."""
    try:
        bids = []
        table = soup.find('tbody', {'id': 'bidSearchResultsForm:bidResultId_data'})
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            bid_solicitation = cells[0].text.strip()
            buyer = cells[1].text.strip()
            description = cells[2].text.strip()
            bid_opening_date = cells[3].text.strip()

            bid_link = base_url + cells[0].find('a')['href']
            bid_data = {
                "Bid Solicitation #": bid_solicitation,
                "Buyer": buyer,
                "Description": description,
                "Bid Opening Date": bid_opening_date,
                "Link": bid_link
            }
            bids.append(bid_data)
        return bids
    except Exception as e:
        logging.error(f"An error occurred in function => extract_bid_data: {str(e)}")

# Function to extract text from the table until "Bill-to Address"
def extract_detailed_info(soup):
    try:
        data = {}
        header_info = {}
        current_section = None
        
        # Find the table containing the header information
        table = soup.find('table', class_='table-01')
        if not table:
            return data
        
        # Iterate through the rows of the table
        rows = table.find_all('tr')
        for row in rows:
            section_header = row.find('td', class_='sectionHeader-02')
            if section_header:
                current_section = section_header.get_text(strip=True)
                if current_section == "Header Information":
                    continue
            if current_section == "Header Information":
                cells = row.find_all('td')
                if len(cells) == 6:
                    header_info[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
                    header_info[cells[2].get_text(strip=True)] = cells[3].get_text(strip=True)
                    header_info[cells[4].get_text(strip=True)] = cells[5].get_text(strip=True)
                elif len(cells) == 4:
                    header_info[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
                    header_info[cells[2].get_text(strip=True)] = cells[3].get_text(strip=True)
                elif len(cells) == 2:
                    header_info[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)
            if row.find('td', text='Bill-to Address:'):
                break
        
        data['Header Information'] = header_info
        return data
    except Exception as e:
        logging.error(f"An error occurred in function => extract_detailed_info: {str(e)}")

def download_attachments(bid, folder_path):
    """Download all attachments for a given bid and save them to the specified folder."""
    try:
        soup = get_soup(bid["Link"])
        attachments = soup.find_all('a', {'class': 'link-01'})
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        for attachment in attachments:
            # Extract file ID from the href attribute
            try:
                file_id = attachment['href'].split("('")[1].split("')")[0]
                attachment_name = attachment.text.strip()
                attachment_url = f"{base_url}/bso/downloadFile.xhtml?docId={file_id}"
                attachment_path = os.path.join(folder_path, attachment_name)
                
                logging.info(f"Downloading {attachment_name} from {attachment_url} to {attachment_path}")
                
                with requests.get(attachment_url) as response:
                    response.raise_for_status()
                    with open(attachment_path, 'wb') as f:
                        f.write(response.content)
            except:
                pass
    except Exception as e:
        logging.error(f"An error occurred in function => download_attachments: {str(e)}")
def main():
    """Main function for scraping process."""
    try:
        all_bids = []
        page = 1
        output_folder ='case1_output'
        os.makedirs(output_folder, exist_ok=True)
        unique_bids = set()  # Track unique bids by their 'Bid Solicitation #' across all pages
        
        while True:
            logging.info(f"Scraping page {page}")
            url = search_url + f"&page={page}"
            logging.info(f"URL: {url}")
            soup = get_soup(url)
            bids = extract_bid_data(soup)
            
            if not bids:
                logging.info("No more bids found. Exiting.")
                break
            
            for bid in bids:
                if bid["Bid Solicitation #"] in unique_bids:
                    logging.info(f"Found bid {bid['Bid Solicitation #']} in earlier pages. Stopping further processing.")
                    break
                
                logging.info(f"Processing bid: {bid['Bid Solicitation #']}")
                folder_path = os.path.join(output_folder, bid["Bid Solicitation #"])
                download_attachments(bid, folder_path)
                
                # Extract detailed information using the bid link
                detailed_info = extract_detailed_info(get_soup(bid["Link"]))
                
                all_bids.append({
                    "Basic Info": bid,
                    "Detailed Info": detailed_info
                })
                
                unique_bids.add(bid["Bid Solicitation #"])
            
            # Check if we need to stop further scraping
            if bid["Bid Solicitation #"] in unique_bids:
                logging.info(f"Found bid {bid['Bid Solicitation #']} in earlier pages. Stopping further scraping.")
                break
            
            page += 1
        output_file_path = os.path.join(output_folder, 'bids.json')
        
        with open(output_file_path, 'w') as f:
            json.dump(all_bids, f, indent=4)
        
        logging.info("Scraping complete. Data saved to case1_output/bids.json.")
        
    except Exception as e:
        logging.error(f"An error occurred in function => main: {str(e)}")

if __name__ == "__main__":
    main()
