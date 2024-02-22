import pandas
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
 
def visualize_data(df, category):
    # Create a figure object with two subplots
    fig, axs = plt.subplots(1, 2, figsize=(12, 6))
 
    # Create a histogram of ratings on the first subplot
    sns.histplot(df['Rating'].replace('N/A', None).dropna().astype(float), bins=15, kde=True, ax=axs[0])
    axs[0].set_title(f'Distribution of Ratings for {category}')
    axs[0].set_xlabel('Rating')
    axs[0].set_ylabel('Frequency')
 
    # Create a bar plot for genres on the second subplot
    genre_counts = df['Genre'].value_counts()
    sns.barplot(x=genre_counts.values, y=genre_counts.index, ax=axs[1])
    axs[1].set_title(f'Number of {category} in Each Genre')
    axs[1].set_xlabel('Count')
    axs[1].set_ylabel('Genre')
 
    # Adjust layout and show the plots
    plt.tight_layout()
    st.pyplot(fig)  # Pass the figure object to st.pyplot
    
 
