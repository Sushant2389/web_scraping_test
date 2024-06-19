import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os

# Create a 'logs' directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')
    
# Set up logging
log_file = os.path.join('logs', 'case2_log.txt')
os.makedirs(os.path.dirname(log_file), exist_ok=True)  

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Base URL of the staff directory
base_url = "https://isd110.org/our-schools/laketown-elementary/staff-directory"

def get_soup(url):
    """Fetch the content of the given URL and return a BeautifulSoup object."""
    try:
        response = requests.get(url)
        return BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        logging.error(f"An error occurred in function =>  get_soup: {str(e)}")

def extract_staff_info(soup):
    try:
        """Extract staff information from the given BeautifulSoup object."""
        staff_list = []
        staff_items = soup.find_all('div', class_='views-row')
        school_name = soup.title.text.split('|')[1].strip()

    # Extract address, state, city, zip
        address_elem = soup.find('p', class_='address')
        if address_elem:
            address_lines = address_elem.get_text().split('\n')
            address = address_lines[1].strip()  # First line is the address
            state_zip = address_lines[2].strip()  # Second line is state and zip
            city = state_zip.split(',')[0].strip()
            state_zip_ = state_zip.split(',')[1].strip()
            state, zip_code = state_zip_.split()  # Split state and zip
        else:
            address = ""
            state = ""
            city = ""
            zip_code = ""
            
        for item in staff_items:
            name = item.find('h2', class_='title').text.strip()
            first_name = name.split(',')[0].strip()
            last_name  = name.split(',')[1].strip()
            title = item.find('div', class_='field job-title').text.strip()
            phone = item.find('div',class_='field phone').text.strip()
            email = item.find('div',class_='field email').text.strip()
            
            staff_data = {
            "School Name": school_name,
                "Address": address,
                "City":city,
                "State": state,
                "Zip": zip_code,
                "First Name": first_name,
                "Last Name": last_name,
                "Title": title,
                "Phone": phone,
                "Email": email
            }
            staff_list.append(staff_data)
        
        return staff_list
    except Exception as e:
        logging.error(f"An error occurred in function => extract_staff_info: {str(e)}")
        return None
    
def scrape_staff_directory(url):
    """Scrape staff directory from the given URL."""
    try: 
        all_staff = []
        page = 0
        
        while True:
            current_url = f"{url}?page={page}"
            logging.info(f"Scraping {current_url}")
            soup = get_soup(current_url)
            staff = extract_staff_info(soup)
            
            if not staff:
                logging.info(f"No more staff found on page {page}. Exiting.")
                break
            
            all_staff.extend(staff)
            page += 1
        
        return all_staff
    except Exception as e:
        logging.error(f"An error occurred in function => scrape_staff_directory: {str(e)}")

def save_to_csv(data, filename):
    """Save data to CSV file."""
    try:
        output_folder ='case2_output'
        os.makedirs(output_folder, exist_ok=True)
        filepath = os.path.join(output_folder, filename)
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
    except Exception as e:
        logging.error(f"An error occurred in function => save_to_csv : {str(e)}")

def main():
    try:
        staff_url = base_url
        staff_data = scrape_staff_directory(staff_url)
        save_to_csv(staff_data, "staff_directory.csv")
    except Exception as e:
        logging.error(f"An error occurred in function => main : {str(e)}")
        
if __name__ == "__main__":
    main()
