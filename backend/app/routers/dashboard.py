from fastapi import APIRouter
from app.models.date_filter import DateFilters
from app.models.overview_metric_model import OverViewMetric
from typing import List
from app.utils.db_conn import POSTS, COMMENTS, USERS, RESPONSE

router = APIRouter(tags=["Dashboard"])

def get_total_users(start_date, end_date):
  
  query = {
    "created_at":{
      "$gte": start_date,
      "$lte": end_date
    }
  }
  
  try:
    count = USERS.count_documents(query)
  except:
    count = 0
  return OverViewMetric(label= "Total Users", delta= None, value= count, help= "This is the total number of users in the selected date range.")

def get_total_comments(start_date, end_date):
  
  query = {
  "commented_date":{
    "$gte": start_date,
    "$lte": end_date
    }
  }
  
  try:
    count = COMMENTS.count_documents(query)
  except:
    count = 0
  return OverViewMetric(label= "Total Comments", delta= None, value= count, help= "This is the total number of comments in the selected date range.")

def get_total_posts(start_date, end_date):
  
  query = {
    "created_at":{
      "$gte": start_date,
      "$lte": end_date
    }
  }
  
  try:
    count = POSTS.count_documents(query)
  except:
    count = 0 
  return OverViewMetric(label= "Total Posts", delta= None, value= count, help= "This is the total number of posts in the selected date range.")

def get_overall_sentiment(start_date, end_date):
  pipeline = [
    {
        "$match": {
            "commented_date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
    },
    {
        "$group": {
            "_id": "$sentiment",
            "count": { "$sum": 1 }
        }
    },
    {
      "$sort":{
        "count": -1
      }
    },
    {
        "$project": {
            "sentiment": "$_id",
            "count": 1,
            "_id": 0
        }
    }
  ]
    
  results = list(COMMENTS.aggregate(pipeline))
  
  if not results:
    return OverViewMetric(label= "Trending Sentiment", delta= None, value= None, help= "No sentiment data found in the selected date range.")
  
  trending_sentiment = results[0]
  value = trending_sentiment.get('sentiment', 'NA')
  count = trending_sentiment.get('count', 0)
  
  return OverViewMetric(label= "Trending Sentiment", delta= value, value= count, help= "This is the trending sentiment of the comments in the selected date range.")


@router.post("/overview_metrics", response_model=List[OverViewMetric])
async def overview_metrics(req: DateFilters):
  return [
    get_total_posts(req.start_date, req.end_date),
    get_total_comments(req.start_date, req.end_date),
    get_total_users(req.start_date, req.end_date),
    get_overall_sentiment(req.start_date, req.end_date)
  ]
