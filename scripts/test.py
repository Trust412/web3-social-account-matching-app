from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from pymongo import MongoClient
from dotenv import load_dotenv
import csv
import os
import random

# Load environment variables
load_dotenv()
uri = os.getenv('MONGODB_URI')

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
arkham_url = "https://platform.arkhamintelligence.com/explorer/address/"
debank_url = "https://debank.com/profile/"

#fetch wallet addresses from mongodb atlas
def fetch_wallet_addresses(skip, limit):
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(uri)
        
        # Select the database and collection
        db = client["web3_social_matching"]
        collection = db["ethereum_wallet_addresses"]
        
        # Fetch documents with pagination
        cursor = collection.find().skip(skip).limit(limit)  # Skip and limit
        
        # Process and print the results
        results = list(cursor)  # Convert cursor to list for easier handling
        return results
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        client.close()
    
# Function to scrape arkham intelligence for twitter
def scrape_arkham_intelligence(wallet_address):
    driver.get(arkham_url + wallet_address)

    # Retry mechanism for loading the page
    success = False
    while not success:
        print("Retrying to load the page...")
        try:
            # Use explicit wait to check for the presence of target divs
            target_divs = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.Header_content__uLJ_E'))
            )

            # Process only the first target div
            if target_divs:
                target_div = target_divs[0]

                # Get Twitter Address
                twitter_address = None
                a_tags = target_div.find_elements(By.TAG_NAME, 'a')
                
                for a_tag in a_tags:
                    link = a_tag.get_attribute('href')
                    if link and link.startswith('https://twitter.com/'):
                        twitter_address = link
                        break  # Exit after finding the first Twitter link
                if twitter_address:
                    return twitter_address
                else:
                    return None

        except Exception as e:
            print(f"An error occurred while loading the page for {wallet_address}: {e}")
            print("Retrying...")
            driver.get(url + wallet_address)  # Retry loading the same page

# Function to scrape debank for twitter
def scrape_debank(wallet_address):
# Loop through each wallet address
    driver.get(debank_url + wallet_address)
    # Retry mechanism for loading the page
    success = False
    while not success:
        try:
            # Use explicit wait to check for the presence of target divs
            a_tags = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, 'a')) # type: ignore
            )
            for a_tag in a_tags:
                link = a_tag.get_attribute('href')
                if link and link.startswith('https://x.com/'):
                    twitter_address = link 
                    break  # Exit after finding the first Twitter link
                else:
                    twitter_address = None  # Twitter address not found
            # Save result if Twitter address is found
            if twitter_address:
                return twitter_address
            else:
                return None
        except Exception as e:
            print(f"An error occurred while loading the page for {wallet_address}: {e}")
            print("Retrying...")
            sleep(random.uniform(0.5, 1.5))
        
# Main function
def main():
    limit = 5  # Number of documents per page
    page_number = 0  # Start at the first page

    while True:
        skip = page_number * limit  # Calculate how many documents to skip
        results = fetch_wallet_addresses(skip, limit)

        if not results:
            print("No more documents to fetch.")
            break
        
        # Display the fetched results
# Assuming results is a list of documents fetched from MongoDB
        for document in results:
            # Print the wallet address in a formatted way
            print(f"Wallet Address: {document['wallet_address']}") # Replace with your processing logic
            twitter_address = scrape_arkham_intelligence(document['wallet_address'])
            if twitter_address == None:
                twitter_address = scrape_debank(document['wallet_address'])
            with open('results.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([document['wallet_address'], twitter_address])
            
        # Ask user if they want to continue after read 10000 addresses
        page_number += 1
        if page_number%20 == 0:
          user_input = input("Press 'y' to continue or 'q' to quit: ")
          if user_input.lower() == 'y':
              continue
          if user_input.lower() == 'n':
              break

if __name__ == "__main__":
    main()