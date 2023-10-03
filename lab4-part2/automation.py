import praw
import pandas as pd
import datetime
import time
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
import mysql.connector
import numpy as np
import threading
import warnings
import sys
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import wordnet
nltk.download('averaged_perceptron_tagger',quiet=True)
nltk.download('wordnet',quiet=True)
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import matplotlib
import matplotlib.pyplot as plt
from sklearn import preprocessing
import tkinter as tk
matplotlib.use('TkAgg')
warnings.filterwarnings("ignore")

period = int(float(sys.argv[1])*60)

#CREATE A PRAW ACCOUNT
client_id = 'bemfBVYTm43pdmtr3fJm_w'
client_secret = '-SXiX9bhOoGlaXDnxbcW8q4IHZqC3w'
user_agent = 'dsci560-lab4 (by /u/anoooody)'
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

def mask_username(username):
    return username[:3] + '*' * len(username[3:])

def get_keywords_and_topics(title):
    words = word_tokenize(title)
    filtered_words = [word for word in words if word.lower() not in stopwords.words('english')]
    nouns = [word for word, pos in pos_tag(filtered_words) if pos.startswith('NN')]
    nouns = ", ".join(nouns)
    filtered_words = ", ".join(filtered_words)
    return pd.Series([filtered_words, nouns], index=['Keywords', 'Topics'])

# Define a function to fetch a batch of posts
def fetch_posts(limit, after=None):
    if after is None:
        submissions = subreddit.new(limit=limit)
    else:
        submissions = subreddit.new(limit=limit, params={'after': after})

    return submissions

def create_dataframe(subreddit, post_amount):
    if background_event.is_set():
        posts = []
        print("Fetching data...")
        
        # Initialize variables
        remaining_posts = post_amount
        after_token = None

        # Keep fetching posts until we reach the desired post_amount or run out of posts
        while remaining_posts > 0:
            batch_size = min(remaining_posts, 1000)
            submissions = fetch_posts(batch_size, after_token)

            for submission in submissions:
                created_utc_timestamp = submission.created_utc
                created_utc_datetime = datetime.datetime.utcfromtimestamp(created_utc_timestamp)
                created_utc_str = created_utc_datetime.strftime('%Y-%m-%d %H:%M:%S')
                title = submission.title
                title_without_special_chars = re.sub(r'[^a-zA-Z0-9\s]', '', title)
                post_info = {
                    "Username": submission.name,
                    'Title': title_without_special_chars.lower(),
                    'URL': submission.url,
                    'Timestamp': created_utc_str,
                    'Post ID': submission.id,
                    'Num of Comments': submission.num_comments,
                    'Upvote Ratio': submission.upvote_ratio
                }
                posts.append(post_info)

            remaining_posts -= batch_size
            after_token = submission.name

        # Create or update the DataFrame
        df = pd.DataFrame(posts)
        print("Pre-processing data...")
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Username'] = df['Username'].apply(mask_username)
        df[['Keywords', 'Topics']] = df['Title'].apply(get_keywords_and_topics)
        
        # Storing to Database
        print("Updating database...")
        store_db(df)
        
        return df
    
def kmeans(embeddings, df, doc_model, user_input):
    # Use the Elbow method to determine the best number of clusters
    cluster_range = range(1, 11)
    sse = []
    for n in cluster_range:
        kmeans = KMeans(n_clusters=n)
        kmeans.fit(preprocessing.normalize(embeddings))
        sse.append(kmeans.inertia_)

    # Use the embedded data obtained previously for KMeans clustering
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters)
    clusters = kmeans.fit_predict(embeddings)

    # Add clustering results to the data frame
    df['Cluster'] = clusters

    # Use TF-IDF to get the keywords of each cluster
    texts = df.groupby('Cluster').apply(lambda x: ' '.join(x['Keywords']))
    vectorizer = TfidfVectorizer(max_df=0.85, stop_words='english', max_features=10)
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    # Get the keywords of each cluster
    keywords = []
    for i in range(n_clusters):
        word_list = tfidf_matrix[i].toarray().argsort()[0][-10:][::-1]
        keywords.append([feature_names[word] for word in word_list])

    # Visualize results
    for i in range(n_clusters):
        print(f"Cluster {i + 1}:\n")
        print("Sample messages from this cluster:")
        sample_messages = df[df['Cluster'] == i]['Title'].sample(5)
        for message in sample_messages:
            print(f"- {message}")
        print("\n")

    # Create a figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    #Add figure for finding best num of clusters
    axs[0, 0].plot(cluster_range, sse, marker='o', linestyle='--')
    axs[0, 0].set_xlabel('Number of clusters')
    axs[0, 0].set_ylabel('SSE')
    axs[0, 0].set_title('Elbow Method')
    
    # Use matplotlib to visualize clustering results
    axs[0, 1].scatter(np.array(embeddings)[:, 0], np.array(embeddings)[:, 1], c=clusters, cmap='rainbow')
    axs[0, 1].set_title("Clustering of Reddit messages")

    # Visualize results using WordCloud in the top-right subplot
    wordcloud = WordCloud()
    axis0 = 1
    axis1 = 0
    for i in range(n_clusters):
        print(f"Cluster {i + 1} keywords: {', '.join(keywords[i])}\n")
        # Generate word cloud for each cluster
        wordcloud = WordCloud(width=400, height=200, background_color='white').generate(' '.join(keywords[i]))
        axs[axis0, axis1].imshow(wordcloud, interpolation='bilinear')
        axs[axis0, axis1].set_title(f"Cluster {i + 1} WordCloud")
        if i == n_clusters-1:
            break
        axis0 = 1
        axis1 = 1

    # You can adjust the spacing between subplots using subplots_adjust
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1, wspace=0.2, hspace=0.2)  # Adjust wspace and hspace

    print("Finding nearest cluster...")
    vector = doc_model.infer_vector(user_input.split())
    vector = np.array(vector, dtype=np.float16)
    closest_cluster = kmeans.predict(vector.reshape(1, -1))[0]
    print("Closest cluster is cluster #: ", closest_cluster+1)
    print("Sample messages from this cluster:")
    sample_messages = df[df['Cluster'] == int(closest_cluster)]['Title'].sample(5)
    for message in sample_messages:
        print(f"- {message}")
    print("\n")
            
    # Show the figures
    plt.show()

def doc2vec(preprocessed_df):
    nltk.download('averaged_perceptron_tagger',quiet=True)
    nltk.download('wordnet',quiet=True)
    reddit_data = preprocessed_df
    # Create an instance of WordNetLemmatizer
    lemmatizer = WordNetLemmatizer()

    # Create an instance of PorterStemmer
    stemmer = PorterStemmer()

    # Function to determine the wordnet pos tag for tokens
    def get_wordnet_pos(treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    tagged_data = []
    for index, row in reddit_data.iterrows():
        text = row['Keywords']

        # Tokenize the text
        tokens = nltk.word_tokenize(text)

        # Get the pos tagging for the tokens
        tagged_tokens = nltk.pos_tag(tokens)

        # Lemmatize the tokens based on their pos tags
        lemmatized_tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in tagged_tokens]

        # Stem the lemmatized tokens
        stemmed_tokens = [stemmer.stem(word) for word in lemmatized_tokens if word != ',']

        # Use the post's ID as a tag for the TaggedDocument
        post_id = row['Post ID']

        tagged_data.append(TaggedDocument(words = stemmed_tokens, tags = [post_id]))

    # VECTOR_SIZE: Determines the dimensionality of the document vectors that the model will learn.
    # WINDOW: Controls the maximum distance between the current word and the predicted word within a document
    # (ex: considers five words to the left and the right of the current word)
    # MIN_COUNT: threshold for the number of times a word can appear in the corpus
    # WORKERS: How many CPU cores to use for parellelization during training
    # EPOCHS: number of times the entire dataset is passed through the model during training.

    model = Doc2Vec(vector_size = 100, window = 5, min_count = 5, workers = 4, epochs = 20)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples = model.corpus_count, epochs = model.epochs)

    # Getting the embeddings for the posts
    embeddings = []
    posts = 0
    for doc in tagged_data:
        post_id = doc.tags[0]
        embedding = model.dv[post_id]  # Get the embedding for the current post
        embeddings.append(embedding)

    return embeddings, model

#Function to store to database
def store_db(df):
    # Establishing a connection to the database
    # Note: Change user name and password if needed
    try:
        # conn = mysql.connector.connect(
        #     host='localhost',
        #     user='root',
        #     password='Dsci560@1234',
        # )

        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='000112Cky&',
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
    except:
        return None

# Define a function to fetch, process, and store posts to database periodically
def update_database(subreddit, post_amount,background_event):
    global df
    while True:
        # Check if background fetching is active
        if background_event.is_set():
            time.sleep(period)  #Fetching period
            df = create_dataframe(subreddit, post_amount)  
        else:
            time.sleep(1)  # Sleep for 1 second when not fetching in the background

#Function to get user input and find nearest cluster
def nearest_cluster(background_event, df):
    time.sleep(3)
    while True:
        if background_event.is_set():
            user_input = input("Type 'quit' to stop updating database:\n")
            if user_input.lower() == 'quit':
                background_event.clear()
        else:
            background_event.clear()
            user_input = input("Enter keywords or a message: ")
            print("User entered:", user_input)
            
            #Create Doc2Vec embeddings
            print("Creating Doc2Vec embeddings...")
            embeddings, doc_model = doc2vec(df)
            #K means Clustering
            print("Generating clusters...")
            kmeans(embeddings, df, doc_model, user_input)

        time.sleep(1)

if __name__ == '__main__':
    # ASKING THE USER HOW MANY POST THEY WANT TO SEE
    user_input = input("Please enter the amount of post you want to see as an integer: ")
    post_amount = int(user_input)

    # Specify the subreddit you want to scrape
    subreddit = reddit.subreddit('tech')

    # Ensure you have these resources downloaded
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

    # Create a threading.Event to control background fetching
    background_event = threading.Event()
    background_event.set()  # Set it to True initially to start fetching

    #First scrape
    df = create_dataframe(subreddit, post_amount)

    # Start the first function (fetch_and_process_posts) in a separate thread
    fetch_thread = threading.Thread(target=update_database, args=(subreddit, post_amount, background_event))
    fetch_thread.start()

    # Start the second function (clustering) in a separate thread
    clustering_thread = threading.Thread(target=nearest_cluster, args=(background_event,df))
    clustering_thread.start()
