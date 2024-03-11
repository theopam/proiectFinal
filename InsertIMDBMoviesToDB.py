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


def scrape_movies():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.5'}

    response = requests.get('https://www.imdb.com/chart/top/', headers=headers)

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract JSON data from the script tag
    json_data = soup.find('script', {'id': '__NEXT_DATA__'}).string
    data = json.loads(json_data)['props']['pageProps']['pageData']['chartTitles']

    # Initialize lists to store movie data
    titles = []
    release_years = []
    runtimes = []
    ratings = []
    genres = []

    for movie in data['edges']:
        node = movie['node']
        title = node['titleText']['text']
        year = node['releaseYear']['year']
        runtime = node['runtime']['seconds'] // 60  # Convert seconds to minutes

        # Extract the aggregate rating
        rating = node['ratingsSummary']['aggregateRating'] if 'ratingsSummary' in node else 'N/A'

        # Extract genres and limit to the first genre
        genre = node['titleGenres']['genres'][0]['genre']['text'] if node['titleGenres']['genres'] else 'N/A'

        titles.append(title)
        release_years.append(year)
        runtimes.append(runtime)

        ratings.append(rating)
        genres.append(genre)

    df = pd.DataFrame({
        'Title': titles,
        'Year': release_years,
        'Runtime': runtimes,
        'Rating': ratings,
        'Genre': genres
    })

    return df

def create_database():
    df = scrape_movies()

    # Table name in your database
    table_name = 'movies'
    try:
        # Connect to MySQL server
        connection = pymysql.connect(
            host="130.61.179.184",  # localhost
            user="root",  # root
            password="Wn##bZ8n@TYtN8",
            database='filme',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # Create cursor
        cursor = connection.cursor()

        # Create database if not exists
        database_name = 'filme'
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
        cursor.execute(f"USE {database_name}")

        # Create table if not exists
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS movies (
                       id INT AUTO_INCREMENT PRIMARY KEY,
                       title VARCHAR(255),
                       year VARCHAR(255),
                       runtime VARCHAR(255),
                       rated VARCHAR(255),
                       genre VARCHAR(255)
                       )
                """)

        for index, row in df.iterrows():
            # Prepare SQL query
            sql = f"INSERT INTO {table_name} (title, year, runtime, rated, genre) VALUES (%s, %s, %s, %s, %s)"
            # Execute query with row values
            cursor.execute(sql, (row['Title'], row['Year'], row['Runtime'], row['Rating'], row['Genre']))

        connection.commit()

        print(f'Data inserted into the table "{table_name}" successfully.')
    except Exception as ex:
        print(f'An error occurred while inserting data: {ex}')
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()

if __name__ == "__main__":
   create_database()


     


