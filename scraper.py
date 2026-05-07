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
    title: str = Field(description="The main headline of the news article")
    summary: str = Field(
        description="A 2-3 sentence summary covering who, what, when, where, why. Journalistic tone, factual, no commentary."
    )
    article_type: str = Field(
        default="news",
        description="Type: 'news', 'analysis', 'opinion', 'interview', 'report', or 'other'",
    )
    key_points: str = Field(
        default="",
        description="3-7 bullet points with the most important facts, claims, quotes, or data. Each bullet is one self-contained sentence. Always extract key points regardless of article type.",
    )
    author: str = Field(description="Full name of the article author")
    author_url: str = Field(
        default="",
        description="URL to the author's profile or bio page if linked from the article",
    )
    date: str = Field(description="Publication date, preferably ISO format")
    image: str = Field(default="", description="URL of the main article image")
    translated: bool = Field(
        default=False,
        description="Whether the extracted content was translated from another language",
    )


LANG_MAP = {"en": "English", "ua": "Ukrainian"}

EMPTY_RESULT = {
    "title": "",
    "summary": "",
    "article_type": "",
    "key_points": "",
    "author": "",
    "author_url": "",
    "date": "",
    "image": "",
    "translated": False,
    "error": "",
}


def _make_error(error_message: str) -> dict:
    return {**EMPTY_RESULT, "error": error_message}


def _build_instruction(target_lang: str) -> str:
    lang_name = LANG_MAP.get(target_lang, "English")
    return (
        "You are extracting structured data from a news article. Follow these rules strictly.\n\n"
        "--- SUMMARY ---\n"
        "Write a 2-3 sentence summary covering the 5 W's: who, what, when, where, why.\n"
        "Journalistic tone: factual, concise, no fluff, no commentary.\n"
        "If the article is long, include only the most significant finding.\n\n"
        "--- KEY POINTS ---\n"
        "Extract 3-7 bullet points. Each bullet is one self-contained sentence.\n"
        "Always extract key points, regardless of article type.\n"
        "Prefer concrete data (numbers, dates, names) over vague statements.\n"
        "Include notable quotes if the article contains any.\n\n"
        "--- ARTICLE TYPE ---\n"
        "Classify as one of: 'news', 'analysis', 'opinion', 'interview', 'report', 'other'.\n"
        "- 'analysis': explains causes or context behind an event, answers 'why'\n"
        "- 'report': structured informational piece without argumentation\n"
        "- 'opinion': argues a viewpoint or position\n"
        "- 'interview': direct question-and-answer format\n"
        "- 'news': factual event reporting\n\n"
        "--- TRANSLATION ---\n"
        f"If the original article is not in {lang_name}, translate ALL text fields "
        f"(title, summary, key_points, date) to {lang_name}.\n"
        "Preserve paragraph breaks and journalistic tone when translating.\n"
        f"Set translated=true in the response.\n"
        f"If the article is already in {lang_name}, set translated=false.\n\n"
        "--- EXTRACTION PRIORITY ---\n"
        "1. Title (main headline)\n"
        "2. Author (full name)\n"
        "3. Date (publication date, ISO when possible)\n"
        "4. Summary (2-3 sentences, 5 W's)\n"
        "5. Key points (3-7 bullets)\n"
        "6. Article type\n"
        "7. Main image URL\n"
        "8. Author profile URL (only if linked from article)\n\n"
        "Return only valid JSON matching the schema. No explanations, no markdown wrappers."
    )


async def scrape_article(url: str, target_lang: str = "en") -> dict:
    llm_config = LLMConfig(
        provider="deepseek/deepseek-chat",
        api_token=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com/v1",
        temperature=0.1,
    )

    instruction = _build_instruction(target_lang)

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
            return _make_error(result.error_message or "Unknown error during crawl")

        if result.extracted_content:
            extracted = json.loads(result.extracted_content)
            if isinstance(extracted, list) and len(extracted) > 0:
                return extracted[0]
            return extracted

        return _make_error("LLM extracted no content from the page")
