# from typing import List, Dict, Optional
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator, constr
from fastapi import FastAPI
from datetime import datetime
from app.chains import final_chain
from app.utils.db_conn import insert_into_db
from typing import Any, Optional
from app.models.request_model import Request
from app.routers import users, posts, dashboard, comments


app=FastAPI(title="Sentiment Classifier Backend")

app.include_router(dashboard.router)
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(comments.router)

async def sentiment_chain(comment_text: str):  
    print(f'{comment_text=}') 
    return final_chain(comment_text)

@app.post("/classification/")
async def classification(req: Request):

    if not req.comment_date:
        req.comment_date = datetime.now()
        
    if not req.post_date:
        req.post_date = datetime.now()
    
    if not req.post_title:
        req.post_title = "Reply"
    
    result = await sentiment_chain(req.comment_text)
    await insert_into_db(req,result)
    return result

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")
