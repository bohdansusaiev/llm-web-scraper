from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scraper import scrape_article

app = FastAPI(
    title="Adaptive Web Scraper",
    description="Adaptive Web Information Collection using LLMs",
    version="1.0.0",
)


class ScrapeRequest(BaseModel):
    url: str
    language: str = "en"


class ScrapeResponse(BaseModel):
    title: str = ""
    summary: str = ""
    article_type: str = ""
    key_points: str = ""
    author: str = ""
    author_url: str = ""
    date: str = ""
    image: str = ""
    translated: bool = False
    error: str = ""


@app.get("/")
async def root():
    return {"message": "Adaptive Web Scraper API is running. Use POST /scrape"}


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(request: ScrapeRequest):
    try:
        result = await scrape_article(request.url, request.language)
        if "error" in result and result["error"]:
            raise HTTPException(status_code=500, detail=result["error"])
        return ScrapeResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
