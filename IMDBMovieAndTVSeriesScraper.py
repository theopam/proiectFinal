import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import streamlit as st
import sys
import os
from InsertIMDBMoviesToDB import create_database
from InsertIMDBTVSeriesToDB import create_db
from dataVisualization import visualize_data

def scrape_imdb_top_movies():
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
        release_years.append(str(year))
        runtimes.append(str(runtime) + ' min')
        ratings.append(str(rating))
        genres.append(genre)

    df = pd.DataFrame({
        'Title': titles,
        'Year': release_years,
        'Runtime': runtimes,
        'Rating': ratings,
        'Genre': genres
    })

    return df

def scrape_imdb_top_series():
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

def main():
    
    page_bg_img=""" 
    <style>
    [data-testid="stAppViewContainer"] {
    background-image: url("https://images.unsplash.com/photo-1505775561242-727b7fba20f0?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D");
    background-size: cover;
    }
    

    [data-testid="stHeader"] {
    background-color: rgba(0, 0, 0, 0);
    }

    [data-testid="stToolbar"] {
    right: 2rem
    }
    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.title('IMDB Scraper')

    # Option to select movies or TV series
    scrape_option = st.selectbox('Select Category', ['Top Movies', 'Top TV Series'])
    #insert_option = st.selectbox('Select Category', ['Top Movies', 'Top TV Series'])

    col1, col2, col3 = st.columns(3) 
     

    if col1.button('IMDB Scrape'):
        with st.spinner('Scraping...'):
            if scrape_option == 'Top Movies':
                df = scrape_imdb_top_movies()
            else:
                df = scrape_imdb_top_series()

            st.success('Scraping Done!')
            st.dataframe(df)

    if col2.button('Database Insert'):
        with st.spinner('Inserting...'):
            if scrape_option == 'Top Movies':
                create_database()
            else:
                create_db()

            st.success('Inserted!')


    if col3.button('Data Visualization'):
        with st.spinner('Creating view...'):
            if scrape_option == 'Top Movies':
                df = scrape_imdb_top_movies()
            else:
                df = scrape_imdb_top_series()
 
            visualize_data(df, 'Movies' if scrape_option == 'Top Movies' else 'TV Series')
 
            st.success('Take a look!')

if __name__ == '__main__':
    main()
