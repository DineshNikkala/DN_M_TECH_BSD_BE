from fastapi import FastAPI, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from Main import biker_safety_detection 
import os

App = FastAPI()

# Configure CORS
origins = [
    "http://localhost:4200", 
    "http://localhost:3000", 
]

App.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)


class FilePathRequest(BaseModel):
    Text: str

@App.get("/ServerStatus")
async def root():
    return { "Status": 200, "Message": "Server is running" }

@App.post("/ProcessVideo")
async def process_video(file: UploadFile = File(...)):
    try:
    
        file_location = f"./uploaded_videos/{file.filename}"
        
        with open(file_location, "wb") as f:
            f.write(await file.read())
            
        response = await biker_safety_detection(file_location)
        
        # return  {"info": f"file '{file.filename}' saved at '{file_location}'"}
        print(f"Detection response: {response}")
        return response
    
    except Exception as e:
        return { "message": str(e) }, 500
    
@App.post("/RemoveFiles")
async def remove_files():
    try:
        images_path = "../bsd-fe/src/Images/"
        # video_path = "../bsd-fe/src/Videos/output.mp4"
        
        # os.remove(video_path)
        
        files_removed = []
        for file_name in os.listdir(images_path):
            file_path = os.path.join(images_path, file_name)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_removed.append(file_name)
                
        if not files_removed:
            return {"message": "No files found in the folder to remove."}

        return {"message": "Files removed successfully.", "files_removed": files_removed}
    
    except Exception as e :
        return { "message": str(e) }, 500