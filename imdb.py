import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly as px
import requests
import json
from bs4 import BeautifulSoup
from collections import Counter
import streamlit as st 

def web_scrape():
    URL= 'https://www.imdb.com/chart/top/?sort=release_date%2Cdesc'
    header= {
        'User_Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        }
    response= requests.get(URL, headers=header)
    soup= BeautifulSoup(response.content,'html.parser')
    
    # Locate the script tag or element that contains the JSON
    script_tag = soup.find('script', type='application/json')

    if script_tag:
        json_data = json.loads(script_tag.string)
        
        movie_list = []

        # Loop through each movie in the JSON structure
        for movie in json_data['props']['pageProps']['pageData']['chartTitles']['edges']:
            node = movie['node']
            
            # Extracting fields
            title = node['titleText']['text']
            rank = movie['currentRank']
            release_year = node['releaseYear']['year']
            rating = node['ratingsSummary']['aggregateRating']
            vote_count= node['ratingsSummary']['voteCount']
            genres = [genre['genre']['text'] for genre in node['titleGenres']['genres']]
            
            # Append the data to the list
            movie_list.append({
                'Rank': rank,
                'Title': title,
                'Release Year': release_year,
                'Rating': rating,
                'voteCount': vote_count,
                'Genres': ', '.join(genres)
            })
            
        # Convert the list into a DataFrame
        df = pd.DataFrame(movie_list)
        return df
    
    else:
        print("No JSON data found in script tags.")

df = web_scrape()

def capping_outliers(df, lower_limit=None, upper_limit=8.6):
    # Calculate upper and lower limits if not provided
    if upper_limit is None:
        upper_limit = df["Rating"].mean() + 3 * df["Rating"].std()
    
    if lower_limit is None:
        lower_limit = df["Rating"].mean() - 3 * df["Rating"].std()

    # Apply the capping
    df["Rating"] = np.where(df["Rating"] > upper_limit,
                            upper_limit,
                            np.where(df["Rating"] < lower_limit,
                                     lower_limit,
                                     df["Rating"]))

    return df
df_capped= capping_outliers(df)

df_cleaned = df.dropna(subset=['Genres', 'Rating'])
df_cleaned['Genres'] = df_cleaned['Genres'].apply(lambda x: x.split(',')[0])

numeric_df = df.select_dtypes(include=['number'])

st.title("Web Scraping Movie Data from IMDB")
tab1, tab2, tab3, tab4 = st.tabs(["About 🏠", "Show DataFrame 📇", "Data Visualization 📈", "Conclusion 💾"])

with tab1:
    st.header('About This Project:')
    st.write('''In this project, I am scraping IMDb data to analyze trends, focusing on average ratings by genre.
              Using Python and libraries like BeautifulSoup or Scrapy, I extract key information such as movie titles, genres, voting counts, and ratings.
             The data is processed to uncover insights and provide a deeper understanding of genre-based ratings trends.''')

with tab2:
    st.markdown("# Extracted Data from IMDB 📇")
    if st.button("Scrape Data"):
        with st.spinner("Scraping data..."):
            df = web_scrape()
            st.success("Data scraped successfully!")
            st.dataframe(df)

with tab3:
    st.markdown("# Data Visualization 💹")
    option = st.selectbox('Select the Option', 
                          ('Boxplot', 'Lineplot', 'Scatterplot'),
                            index=None,
                            placeholder="Select One",)
    st.write('You Selected:', option)

    
    if option == 'Boxplot':
        st.subheader("Boxplot of IMDb Ratings by Genre ")
        avg_rating_by_genre = df_cleaned.groupby('Genres')['Rating'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.boxplot(x='Genres', y='Rating', data=df_cleaned, palette='viridis', ax=ax)
        ax.set_title('IMDb Ratings Boxplot by Genres', fontsize=16)
        ax.set_xlabel('Genres', fontsize=12)
        ax.set_ylabel('Rating', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        st.pyplot(fig)

    elif option == 'Lineplot':
        st.subheader("Average IMDb Ratings Over the Years")
        avg_rating_by_year = df_capped.groupby('Release Year')['Rating'].mean().reset_index()
        plt.figure(figsize=(10,6))
        sns.lineplot(x='Release Year', y='Rating', data=avg_rating_by_year, marker='o')
        plt.title('Average IMDb Ratings Over the Years')
        plt.xlabel('Release Year')
        plt.ylabel('Average Rating')
        plt.grid(True)
        st.pyplot(plt)

    elif option == 'Scatterplot':
        st.subheader('Scatter Plot for Rating vs. Vote Count ')
        plt.figure(figsize=(10,6))
        sns.scatterplot(x='voteCount', y='Rating', data=df_capped, hue='Genres', palette='tab10', legend=False)
        plt.title('IMDb Rating vs. Vote Count')
        plt.xlabel('Vote Count')
        plt.ylabel('Rating')
        plt.xscale('log')  
        st.pyplot(plt)
     
  
with tab4:
    st.markdown("# Conclusion 💾")
    st.write('''In this project, IMDb data was scraped and analyzed to explore trends in movie ratings by genre. We can use Python’s BeautifulSoup library to extract data and pandas to clean and analyze it.''')
    
    st.subheader('Key Findings on Genre:')
    
    st.markdown('''
    - Genre Performance: Crime, Drama, and Horror genres received consistently higher ratings than Film-Noir and Biography, indicating stronger audience appeal for the former.
    - Temporal Trends: Movies released between 1940 and 1960 maintained high ratings, averaging around 8.0, while ratings saw a significant increase from 1970 to 2000, reflecting changing audience preferences.
    - Vote Count and Ratings Relationship: The scatter plot analysis showed a clear positive correlation between vote count and ratings, suggesting that films with more audience engagement typically received higher ratings.''')

    st.write('''These insights highlight the importance of both audience engagement and genre appeal in shaping movie ratings on IMDb.''')        