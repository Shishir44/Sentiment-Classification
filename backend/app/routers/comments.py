from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime
from app.models.date_filter import DateFilters
from app.utils.db_conn import POSTS, COMMENTS, USERS

router = APIRouter(tags=["Comments"])

# Helper function to fetch post details
def get_post_details(post_id: int):
    try:
        post = POSTS.find_one(
            {"post_id": post_id},
            {
                "post_title": 1, 
                "post_caption": 1, 
                "created_at": 1
                }
        )
        
        if not post:
            raise ValueError(f"Post with post_id {post_id} not found")
        
        return {
            "post_title": post["post_title"],
            "post_caption": post["post_caption"],
            "created_at": post["created_at"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching post details: {e}")


# Helper function to get paginated comments using aggregation pipeline
def get_paginated_comments(post_id: int, start_date: datetime, end_date: datetime, page_no: int, documents_per_page: int) -> Dict[str, Any]:
    # Pipeline to count total matching documents
    total_docs_pipeline = [
        {
            "$match": {
                "post_id": post_id, 
                    "commented_date": {"$gte": start_date, "$lte": end_date
                                       }
                                       }
                                       },
        {
            "$count": "total_docs"
            }
    ]
    
    # Get the total document count
    total_docs_result = COMMENTS.aggregate(total_docs_pipeline).to_list(length=None)
    total_docs = total_docs_result[0]["total_docs"] if total_docs_result else 0

    # Calculate the total pages
    total_pages = (total_docs + documents_per_page - 1) // documents_per_page  # Ceiling division

    # Pipeline to get paginated documents
    paginated_pipeline = [
        {"$match": {"post_id": post_id, "commented_date": {"$gte": start_date, "$lte": end_date}}},
        {"$skip": documents_per_page * (page_no - 1)},
        {"$limit": documents_per_page}
    ]
    
    # Retrieve paginated comments
    paginated_comments = COMMENTS.aggregate(paginated_pipeline).to_list(length=None)

    return {
        "current_page": page_no,
        "total_pages": total_pages,
        "total_documents": total_docs,
        "comments": paginated_comments
    }



# Helper function to fetch usernames for a list of user_ids
def get_usernames(user_ids: List[int]):
    try:
        users = USERS.find(
            {"user_id": {"$in": user_ids}},
            {
                "user_id": 1, 
                "user_name": 1
                }
        ).to_list(length=None)
        
        # Create a mapping of user_id to user_name
        return {user["user_id"]: user["user_name"] for user in users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching usernames: {e}")

# Helper function to build the comments data with usernames
def build_comments_data(comments, user_map):
    comments_data = []
    for comment in comments:
        comments_data.append({
            "commented_username": user_map.get(comment["user_id"], "Unknown"),
            "comment_text": comment["comment"],
            "sentiment": comment["sentiment"],
            "commented_date": comment.get("commented_date")
        })
    return comments_data

# Main endpoint to get post details and comments
@router.post("/comments", response_model=dict)
async def get_comments(
    post_id: int,
    req: DateFilters,
    page_no: int=1,
    documents_per_page: int = 10
):
    """
  This endpoint takes in a post_id, date range and a page number, and returns a list of post along with the comments within that date range.
  
  """
    try:

        start_date = req.start_date
        end_date = req.end_date
        # Fetch post details

        post_details = get_post_details(post_id)

        # Fetch comments for the post within the date range
        paginated_comments_data = get_paginated_comments(post_id, start_date, end_date, page_no, documents_per_page)

        # Extract user_ids from comments and fetch corresponding usernames
        user_ids = list(set(comment["user_id"] for comment in paginated_comments_data["comments"]))
        user_map = get_usernames(user_ids)

        # Build comments data with usernames
        comments_data = build_comments_data(paginated_comments_data["comments"], user_map)

        # Return final response with post details and comments
        return {
            "post_details": {
                **post_details,
                "comments": comments_data
            },
            "pagination": {
                "current_page": paginated_comments_data["current_page"],
                "total_pages": paginated_comments_data["total_pages"],
                "total_documents": paginated_comments_data["total_documents"]
            }
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching comments: {e}")
