from fastapi import APIRouter

router = APIRouter(tags=["Users"])

@router.get("/users/")
async def get_user():
  return ""
  