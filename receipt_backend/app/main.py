from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ocr

app = FastAPI()
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ocr.router)


@app.get("/")
async def main():
    print("success")
    return {"main": "success"}
