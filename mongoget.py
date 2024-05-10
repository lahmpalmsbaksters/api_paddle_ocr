from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from fastapi import HTTPException
from bson.objectid import ObjectId

app = FastAPI()

# MongoDB connection setup
myclient = MongoClient("mongodb://admin:islabac123@18.143.76.245:27017/")
mydb = myclient["people_detect_log"]
mycol = mydb["log"]

class LogItem(BaseModel):
    status: str
    time: str

@app.get("/logs/{log_id}", response_model=LogItem)
async def read_log(log_id: str):
    print (log_id)
    log_data = mycol.find_one({"_id": ObjectId(log_id)})
    if log_data is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return LogItem(**log_data)
