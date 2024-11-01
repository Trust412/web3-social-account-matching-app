from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
uri = os.getenv('MONGODB_URI')

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
                    
        # Ask user if they want to go to the next page
        user_input = input("Press 'n' for next page or 'q' to quit: ")
        
        # move to next page mannualy
        if user_input.lower() == 'n':
            page_number += 1  # Move to the next page
        elif user_input.lower() == 'q':
            break  # Exit the loop

if __name__ == "__main__":
    main()