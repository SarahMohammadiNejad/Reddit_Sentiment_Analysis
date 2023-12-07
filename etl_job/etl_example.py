"""
Example file to simulate an ETL process within a docker pipeline
- Extracts from a mongo db
- Transforms the collections
- Loads the transformed collections to postgres db

To be started by docker (see ../docker-compose.yml)
        
For inspecting that ETL worked out: docker exec -it pipeline_example_my_postgres_1 psql -U postgres
"""


import pymongo
import sqlalchemy  # use a version prior to 2.0.0 or adjust creating the engine and df.to_sql()
import psycopg2
import time
import logging
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

# mongo db definitions
client = pymongo.MongoClient('my_mongo', port=27017)  # my_mongo is the hostname (= service in yml file)
db = client.my_db
dbcoll = db.my_collection


# postgres db definitions. HEADS UP: outsource these credentials and don't push to github.
USERNAME_PG = 'postgres'
PASSWORD_PG = 'postgres'
HOST_PG = 'my_postgres'  # my_postgres is the hostname (= service in yml file)
PORT_PG = 5432
DATABASE_NAME_PG = 'reddits_pgdb'

conn_string_pg = f"postgresql://{USERNAME_PG}:{PASSWORD_PG}@{HOST_PG}:{PORT_PG}/{DATABASE_NAME_PG}"

time.sleep(3)  # safety margine to ensure running postgres server
pg = sqlalchemy.create_engine(conn_string_pg)


# Create the table
create_table_string = sqlalchemy.text("""CREATE TABLE IF NOT EXISTS reddits (
                                         date TEXT,
                                         reddit TEXT,
                                         sentiment NUMERIC,
                                         comp NUMERIC,
                                         neu NUMERIC,
                                         pos NUMERIC,
                                         neg NUMERIC
                                         );
                                      """)

pg.execute(create_table_string)

def extract():
    """
    reads collections from a mongo database and converts them into a pandas
    dataframe. 

    Returns
    -------
    new_reddits : pandas dataframe

    """
    new_mongo_docs = dbcoll.find()
    new_reddits = pd.DataFrame.from_records(list(new_mongo_docs))
    n_reddits = new_reddits.shape[0]

    logging.critical(f"\n---- {n_reddits} reddits extracted ----\n")
    logging.info(f"\n---- {n_reddits} reddits extracted ----\n")

    return new_reddits






def transform(new_reddits):
    """
    transforms a dataframe containing reddits in a dictionary to a clean
    dataframe and adds a column for the (dummy/length) sentiment of the reddit

    Parameters
    ----------
    new_reddits : unclean pandas dataframe

    Returns
    -------
    new_reddits_df : cleaned pandas dataframe including "sentiments"
    """
    
    new_reddits_df = pd.DataFrame()


    for _, row in new_reddits.iterrows():

        new_reddits_df = new_reddits_df._append(row['found_reddit'], ignore_index=True)

        print(row['found_reddit'])
    # as a placeholder for the sentiment: add length of reddit to dataframe
    try:
        new_reddits_df['sentiment'] = new_reddits_df['reddit'].str.len()
        senti = new_reddits_df['reddit'].apply(analyser.polarity_scores).apply(pd.Series)

        new_reddits_df['comp'] = senti['compound']
        new_reddits_df['neu'] = senti['neu']
        new_reddits_df['pos'] = senti['pos']
        new_reddits_df['neg'] = senti['neg']

        logging.critical("\n---- transformation completed ----\n")
    except:
        logging.critical("\n---- no reddits to transform ----\n")
       
    
    
    return new_reddits_df



def load(new_reddits_df):
    """
    saves cleaned reddits including their sentiments to a postgres database

    Returns
    -------
    None.

    """
    new_reddits_df.to_sql('reddits', pg, if_exists='replace', index=False)
    # if new_reddits_df.shape[0] > 0:  # only export if new reddits exist
    #     new_reddits_df.to_sql('reddits', pg, if_exists='append', index=False)

    logging.critical("\n---- new reddits loaded to postgres db ----\n") 
    return None



new_reddits = extract()
new_reddits_df = transform(new_reddits)
load(new_reddits_df)



