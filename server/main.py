import logging
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
import os
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS (allow your frontend to communicate with the backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URL = "mongodb+srv://vinnath:ggvinnath@otp.c4pi4.mongodb.net/?retryWrites=true&w=majority&appName=otp"
client = AsyncIOMotorClient(MONGO_URL)
db = client.otp  # 'otp' will be your MongoDB database

# Define a data model for items
class Item(BaseModel):
    name: str
    description: str

# Function to check MongoDB connection
async def check_mongo_connection():
    try:
        # Attempt to list databases to confirm connection
        await client.admin.command('ping')
        logger.info("MongoDB connection successful!")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")

# Run the connection check when the application starts
@app.on_event("startup")
async def on_startup():
    await check_mongo_connection()

# Route to insert an item into the MongoDB collection
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.dict()
    result = await db["items"].insert_one(item_dict)
    logger.info(f"Inserted item with ID: {result.inserted_id}")
    return {"id": str(result.inserted_id)}

# Route to get an item from MongoDB by its ID
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = await db["items"].find_one({"_id": ObjectId(item_id)})
    if item:
        logger.info(f"Fetched item with ID: {item_id}")
        return item
    logger.warning(f"Item with ID: {item_id} not found")
    raise HTTPException(status_code=404, detail="Item not found")

# Basic root route
@app.get("/")
async def read_root():
    logger.info("Root route accessed")
    return {"message": "Welcome to FastAPI with MongoDB!"}
