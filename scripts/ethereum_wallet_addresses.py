import os
from dune_client.client import DuneClient
from dotenv import load_dotenv
import sys
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Atlas connection string
load_dotenv()
uri = os.getenv('MONGODB_URI')

# add description


# Function to save results to MongoDB Atlas
def save_results_to_mongodb(results, query_id):
    try:
        client = MongoClient(uri, server_api=ServerApi('1'))
        db = client['web3_social_matching']
        collection = db['ethereum_wallet_addresses']

        # Convert DataFrame to list of dictionaries
        data_to_insert = results.to_dict('records')

        # Add query_id to each document
        for item in data_to_insert:
            item['query_id'] = query_id

        # Insert the data
        result = collection.insert_many(data_to_insert)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB Atlas")

    except Exception as e:
        print(f"An error occurred while saving to MongoDB: {e}")

    finally:
        client.close()

# Dune Query setup
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

dune = DuneClient.from_env()

# Function to save results as CSV
def save_results_as_csv(results, query_id):
    csv_filename = f"query_{query_id}_results.csv"
    results.to_csv(csv_filename, index=False)
    print(f"Full results saved to {csv_filename}")

# Get id passed in python script invoke
id = sys.argv[1]
print('query id: {}'.format(id))

queries_path = os.path.join(os.path.dirname(__file__), '..', 'queries')
files = os.listdir(queries_path)
found_files = [file for file in files if str(id) == file.split('___')[-1].split('.')[0]]

if len(found_files) != 0:
    query_file = os.path.join(os.path.dirname(__file__), '..', 'queries', found_files[0])

    with open(query_file, 'r', encoding='utf-8') as file:
        query_text = file.read()

    # Run the full query and save results
    print('\nRunning full query and saving results...')
    results = dune.run_sql(query_text)
    full_df = pd.DataFrame(data=results.result.rows)
    
    # Save results to CSV
    save_results_as_csv(full_df, id)

    # Save results to MongoDB Atlas
    save_results_to_mongodb(full_df, id)

    # Print DataFrame info
    print('\n')
    print(full_df.describe())
    print('\n')
    print(full_df.info())
else:
    print('query id file not found, try again')