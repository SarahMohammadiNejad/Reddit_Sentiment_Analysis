# Reddit_Sentiment_Analysis
Here we created a Dockerized Data Pipeline that analyzes the sentiment of reddits.

In this project, you will build a data pipeline that collects reddits and stores them in a database. Next, the sentiment of reddits is analyzed and the annotated text is stored in a second database. steps are:
 - Collect data from reddit
 - Store data in Mongo DB
- Create an ETL job transporting data from MongoDB to PostgreSQL
- Run sentiment analysis on the text



**Important:** you  need to add the username and password of your reddit account and application in "get_reddits.py" file.

*docker-compose build
*docker-compose up

then 
*docker-compose ps -a
to find the name of container related to postgres (POSTGRES_CONTAINER_NAME) and then run 
*docker exec -it POSTGRES_CONTAINER_NAME psql -U postgres
