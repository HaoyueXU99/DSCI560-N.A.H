import praw
import pandas as pd
import datetime
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import mysql.connector
import numpy as np

#CREATE A PRAW ACCOUNT
client_id = 'bemfBVYTm43pdmtr3fJm_w'
client_secret = '-SXiX9bhOoGlaXDnxbcW8q4IHZqC3w'
user_agent = 'dsci560-lab4 (by /u/anoooody)'
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# ASKING THE USER HOW MANY POST THEY WANT TO SEE
user_input = input("Please enter the amount of post you want to see as an integer: ")
post_amount = int(user_input)

# Specify the subreddit you want to scrape
subreddit = reddit.subreddit('tech')
posts = []

# Define a function to fetch a batch of posts
def fetch_posts(limit, after=None):
    if after is None:
        submissions = subreddit.new(limit=limit)
    else:
        submissions = subreddit.new(limit=limit, params={'after': after})

    return submissions

# Initialize variables
remaining_posts = post_amount
after_token = None

# Keep fetching posts until we reach the desired post_amount or run out of posts
while remaining_posts > 0:
    batch_size = min(remaining_posts, 1000)  # Limit batch size to 1000 or remaining_posts, whichever is smaller
    submissions = fetch_posts(batch_size, after_token)

    # Process and collect post information
    for submission in submissions:
        created_utc_timestamp = submission.created_utc
        created_utc_datetime = datetime.datetime.utcfromtimestamp(created_utc_timestamp)
        created_utc_str = created_utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
        title = submission.title
        title_without_special_chars = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        post_info = {
            "Username": submission.name,  # Usernames were already masked
            'Title': title_without_special_chars.lower(),
            'URL': submission.url,
            'Timestamp': created_utc_str,
            'Post ID': submission.id,
            'Num of Comments': submission.num_comments,
            'Upvote Ratio': submission.upvote_ratio
        }
        posts.append(post_info)

    # Update remaining posts and after_token for the next batch
    remaining_posts -= batch_size
    after_token = submission.name  # Store the last post's name as the after token

# CREATING THE DF
df = pd.DataFrame(posts)
print("\nDataFrame after cleaning:")
print(df)

# Ensure you have these resources downloaded
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

def mask_username(username):
    return username[:3] + '*'*len(username[3:])

def get_keywords_and_topics(title):
    # Tokenize and remove stopwords
    words = word_tokenize(title)
    filtered_words = [word for word in words if word.lower() not in stopwords.words('english')]

    # Get nouns as topics
    nouns = [word for word, pos in pos_tag(filtered_words) if pos.startswith('NN')]
    nouns = ", ".join(nouns)
    filtered_words = ", ".join(filtered_words)

    return pd.Series([filtered_words, nouns], index=['Keywords', 'Topics'])

# Convert timestamp
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
# Mask username
df['Username'] = df['Username'].apply(mask_username)
# Get keywords and topics
df[['Keywords', 'Topics']] = df['Title'].apply(get_keywords_and_topics)
print("\nDataFrame after keywords extraction:")
print(df)

# Storing to MYSQL
print("\nStoring to MySQL...")
# Establishing a connection to the database
# Note: Change user name and password if needed
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Dsci560@1234',
)

# Create a cursor to interact with the database
cursor = conn.cursor(buffered=True)

# Ensure the database exists
cursor.execute("CREATE DATABASE IF NOT EXISTS Lab4_NAH")
conn.database = 'Lab4_NAH'

# Drop the table containing stock info if it exists
cursor.execute("DROP TABLE IF EXISTS reddit_posts")

# Create a table for raw stock data if it doesn't already exist
create_table_query = """
CREATE TABLE IF NOT EXISTS reddit_posts (
    Username varchar(50),
    Title text,
    URL text,
    Timestamp datetime,
    Post_ID varchar(20),
    Num_Comments int,
    Upvote_Ratio float,
    Keywords text,
    Topics text
)
"""
cursor.execute(create_table_query)
# Committing any changes made during the initialization
conn.commit()

#Populating table
for i, row in df.iterrows():
    listt = list(row)
    # listt.insert(0,i)
    result = tuple(listt)
    insert = "INSERT INTO reddit_posts values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(insert, tuple(result))

# Commit the changes
conn.commit()

# Close the cursor and database connection
cursor.close()
conn.close()