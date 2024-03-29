import requests
from bs4 import BeautifulSoup
import os
import sys
import json
import pymysql  # Change the import statement
import pandas as pd
from pathlib import Path

# Add the parent directory to sys.path
current_dir = Path(__file__).resolve().parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

def scrape_series():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    response = requests.get('https://www.imdb.com/chart/toptv/', headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Extract JSON data from the script tag
    json_data = soup.find('script', {'id': '__NEXT_DATA__'}).string
    data = json.loads(json_data)['props']['pageProps']['pageData']['chartTitles']

    # Initialize lists to store series data
    titles = []
    periods = []
    episodes_counts = []
    ratings = []
    genres = []

    for series in data['edges']:
        node = series['node']
        title = node['titleText']['text']
        start_year = node['releaseYear']['year']
        end_year = node.get('releaseYear').get('endYear', start_year)
        period = f"{start_year} - {end_year}" if start_year != end_year else str(start_year)
        episodes = node['episodes']['episodes']['total'] if 'episodes' in node and 'episodes' in node['episodes'] else 'N/A'
        rating = node['ratingsSummary']['aggregateRating'] if 'ratingsSummary' in node else 'N/A'
        genre = node['titleGenres']['genres'][0]['genre']['text'] if node['titleGenres']['genres'] else 'N/A'

        titles.append(title)
        periods.append(period)
        episodes_counts.append(episodes)
        ratings.append(str(rating))
        genres.append(genre)

    df_series = pd.DataFrame({
        'Title': titles,
        'Period': periods,
        'Episodes': episodes_counts,
        'Rating': ratings,
        'Genre': genres
    })

    return df_series


def create_db():

    df = scrape_series()

    # Table name in your database
    table_name = 'tvseries'
    try:
        # Connect to MySQL server
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="123bujie",
            database='filme',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # Create cursor
        cursor = conn.cursor()

        # Create database if not exists
        database_name = 'filme'
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE {database_name}")

        # Create table if not exists
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS tvseries (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       title VARCHAR(255),
                       period VARCHAR(255),
                       episodes INT,
                       rated VARCHAR(255),
                       genre VARCHAR(255)
                       )
                """)

        for index, row in df.iterrows():
            # Prepare SQL query
            sql = f"INSERT INTO {table_name} (title, period, episodes, rated, genre) VALUES (%s, %s, %s, %s, %s)"
            # Execute query with row values
            cursor.execute(sql, (row['Title'], row['Period'], row['Episodes'], row['Rating'], row['Genre']))

        conn.commit()

        print(f'Data inserted into the table "{table_name}" successfully.')
    except Exception as ex:
        print(f'An error occurred while inserting data: {ex}')
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()


if __name__ == "__main__":
   create_db()


     


