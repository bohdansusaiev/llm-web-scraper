import os
import json
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler, LLMConfig, CacheMode
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.async_configs import CrawlerRunConfig

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in .env file")


class NewsArticle(BaseModel):
    title: str = Field(description="The headline or title of the news article")
    summary: str = Field(
        description="A detailed, informative summary of the article content (2-4 paragraphs)"
    )
    article_type: str = Field(
        default="news",
        description="Type of article: 'interview', 'news', 'opinion', or 'other'",
    )
    key_points: str = Field(
        default="",
        description="If article_type is 'interview': list of key points, notable quotes, "
                    "and facts from the interview. Otherwise: empty string.",
    )
    author: str = Field(description="The name of the article author")
    author_url: str = Field(
        default="",
        description="URL to the author's profile or bio page if available",
    )
    date: str = Field(description="The publication date of the article")
    image: str = Field(default="", description="URL of the main article image")
    translated: bool = Field(
        default=False,
        description="Whether the extracted content was translated from another language",
    )


LANG_MAP = {"en": "English", "ua": "Ukrainian"}


async def scrape_article(url: str, target_lang: str = "en") -> dict:
    llm_config = LLMConfig(
        provider="deepseek/deepseek-chat",
        api_token=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        temperature=0.1,
    )
    lang_name = LANG_MAP.get(target_lang, "English")
    instruction = (
        "Extract the news article from this page. "
        "First determine the article type: 'interview', 'news', 'opinion', or 'other'. "
        f"Translate all extracted text fields (title, summary, key_points, date) to {lang_name}. "
        "Preserve the original paragraph breaks and text structure when translating. "
        f"Set translated=true if the original article was not in {lang_name}. "
        "Write a detailed, informative summary (2-4 paragraphs). "
        "If the article is an interview, extract key points, notable quotes, "
        "and facts into the key_points field. "
        "Identify the title, author, author profile URL, publication date, "
        "and main image URL. Return only the structured data."
    )

    strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=NewsArticle.model_json_schema(),
        extraction_type="schema",
        instruction=instruction,
        input_format="markdown",
        force_json_response=True,
        verbose=True,
    )

    async with AsyncWebCrawler(verbose=True) as crawler:
        run_config = CrawlerRunConfig(
            extraction_strategy=strategy,
            cache_mode=CacheMode.BYPASS,
            word_count_threshold=10,
            page_timeout=60000,
            wait_until="domcontentloaded",
            verbose=True,
        )
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            error_msg = result.error_message or "Unknown error during crawl"
            return {
                "title": "",
                "summary": "",
                "article_type": "",
                "key_points": "",
                "author": "",
                "author_url": "",
                "date": "",
                "image": "",
                "translated": False,
                "error": error_msg,
            }

        if result.extracted_content:
            extracted = json.loads(result.extracted_content)
            if isinstance(extracted, list) and len(extracted) > 0:
                return extracted[0]
            return extracted

        return {
            "title": "",
            "summary": "",
            "article_type": "",
            "key_points": "",
            "author": "",
            "author_url": "",
            "date": "",
            "image": "",
            "translated": False,
            "error": "LLM extracted no content from the page.",
        }
