"""Optional post-extraction translation pass. Triggered by language='ua' in
the request. Kept separate from extraction so the main prompt stays language-
neutral and benchmarkable."""
import json
import logging

from app.config import SUPPORTED_LANGUAGES
from app.core.llm_extractor import extract as llm_extract
from app.core.prompts import TRANSLATION_INSTRUCTION_TEMPLATE
from app.models.catalog import ScientificPaper

logger = logging.getLogger(__name__)


async def translate_paper(paper: ScientificPaper, target_lang: str) -> ScientificPaper:
    """Translate user-visible text fields. Identity fields (title, authors,
    venue, year, doi) stay in original. Returns the same paper mutated."""
    if target_lang == "en" or target_lang not in SUPPORTED_LANGUAGES:
        return paper

    payload = {
        "abstract": paper.abstract,
        "methodology": paper.methodology,
        "conclusions": paper.conclusions,
        "keywords": paper.keywords,
    }
    if not any([payload["abstract"], payload["methodology"], payload["conclusions"]]):
        # Nothing to translate.
        paper.language = target_lang
        return paper

    instruction = TRANSLATION_INSTRUCTION_TEMPLATE.format(
        target_lang=SUPPORTED_LANGUAGES[target_lang]
    )
    schema = {
        "type": "object",
        "properties": {
            "abstract": {"type": "string"},
            "methodology": {"type": "string"},
            "conclusions": {"type": "string"},
            "keywords": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["abstract", "methodology", "conclusions", "keywords"],
    }

    result = await llm_extract(
        markdown=json.dumps(payload, ensure_ascii=False),
        instruction=instruction,
        schema=schema,
    )
    if not result.success:
        logger.warning("translation failed for %s: %s", target_lang, result.error)
        return paper

    paper.abstract = result.data.get("abstract", paper.abstract) or paper.abstract
    paper.methodology = result.data.get("methodology", paper.methodology) or paper.methodology
    paper.conclusions = result.data.get("conclusions", paper.conclusions) or paper.conclusions
    new_kw = result.data.get("keywords")
    if isinstance(new_kw, list) and new_kw:
        paper.keywords = [str(k).strip() for k in new_kw if str(k).strip()]
    paper.language = target_lang
    return paper
