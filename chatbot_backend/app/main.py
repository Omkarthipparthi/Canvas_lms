import json
import shutil
from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# Assuming chat_gen is in job_matching.py and is the correct import for your setup
from app.job_matching import chat_gen  
from app.chat_gen import chat_gen as CG

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define request and response models
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

# Create an instance of chat_gen
JB_chat_instance = chat_gen()
CG_chat_instance = CG()

@app.post("/ask-pdf", response_model=ChatResponse)
async def ask_pdf_endpoint(question: str = Form(...), file: UploadFile = File(None)):
    try:
        # Process the question using the chat_gen instance
        answer = CG_chat_instance.ask_pdf(question)
        return ChatResponse(answer=answer)
    except Exception as e:
        # If there's an error, return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-pdf/")
async def create_upload_file(file: UploadFile = File(...)):
    # Save the uploaded file to a specified location
    file_location = f"./data/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update the chat_gen instance with the new file path
    try:
        jobs = JB_chat_instance.update_pdf_file_path(file_location)
        print("OMKAR in lOOP")
        
    #     try:
    #         jobs_dict = json.loads(jobs)
    #     except json.JSONDecodeError as e:
    #         print(f"Error decoding JSON: {e}")
    #         # Handle the error or exit the code if necessary
    #     else:
    #         op = ""
    #         for i in jobs_dict:
    #             print(f"Key (i): {i}, Type: {type(i)}")  # Debug print for the key
    #             if isinstance(jobs_dict[i], dict):
    #                 for j in jobs_dict[i]:
    #                     value = jobs_dict[i][j]
    #                     print(f"Subkey (j): {j}, Type: {type(j)}")  # Debug print for the subkey
    #                     print(f"Value: {value}, Type: {type(value)}")  # Debug print for the value
    #                     op += "\n" + str(j) + ": " + str(value) + "\n"
    #             else:
    #                 print(f"Error: The value for key '{i}' is not a dictionary. Actual value: {jobs_dict[i]}, Type: {type(jobs_dict[i])}")



    #     print("OMKAR",op)
        
        return JSONResponse(status_code=200, content={"filename": file.filename, "data": jobs })
    except Exception as e:
            # If there's an error updating the path, return a 500 error
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
