from fastapi import APIRouter
from app.models.date_filter import DateFilters
from app.utils.db_conn import POSTS, COMMENTS

router = APIRouter(tags=["Posts"])

@router.post("/all_posts/")
async def get_all_posts(req: DateFilters, page_number: int = 1, documents_per_page: int = 10):
  """
  This endpoint takes in a date range and a page number, and returns a list of posts within that date range.
  The post id and post title is returned as a list of documents.
  """
  
  match_query = {
    "created_at": {
        "$gte": req.start_date,
        "$lte": req.end_date
    }
  }
  
  total_docs = POSTS.count_documents(match_query)
  num_pages = (total_docs + documents_per_page - 1) // documents_per_page  
  
  pipeline = [
    {
        "$match": match_query
    },
    {
        "$sort": {
            "created_at": -1
        }
    },
    {
        "$project": {
            "_id": 0,
            "post_id": 1,
            "post_title": 1
        }
    },
    {
        "$skip": documents_per_page * (page_number - 1)
    },
    {
        "$limit": documents_per_page
    }
  ]

  docs = list(POSTS.aggregate(pipeline))

  return {
      "current_page": page_number,
      "total_pages": num_pages,
      "total_documents": total_docs,
      "documents": docs
  }
  
@router.post("/individual_post_details")
async def get_individual_post_details(req: DateFilters, post_id: int = 817):
  """
  This endpoint takes in a date range and a post id and returns the details of the post.
  Details include post id, post title, post caption, date of the post, number of comments, and sentiment distribution.
  """
  
  post_details = {}
    
  try:
    post = POSTS.find_one({"post_id": post_id})
    post_id = post.get("post_id", "NA")
    post_title = post.get("post_title", "NA")
    post_caption = post.get("post_caption", "NA")
    post_date = post.get("created_at", "NA")
    
    match_query = {
          "commented_date": {
              "$gte": req.start_date,
              "$lte": req.end_date
            },
          "post_id": post_id
      }
    
    pipeline = [
      {
          "$match": match_query
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
  
    total_comments = COMMENTS.count_documents(match_query)  
    sentiment_result = list(COMMENTS.aggregate(pipeline))
    
    post_details = {
        "post_id": post_id,
        "post_title": post_title,
        "post_caption": post_caption,
        "post_date": post_date,
        "total_comments": total_comments,
        "sentiment_distribution": sentiment_result
    }
    
    return post_details
  except Exception as e:
    return "Error fetching post details: " + str(e)
  
  
