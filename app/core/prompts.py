"""Prompt templates for the generic LLM extractor and the scientific catalog.

Kept in one place so the thesis can quote them verbatim.
Edit here, not inline — it's the most-tuned part of the system."""

# ---------- Generic extraction (POST /scrape) ----------

GENERIC_EXTRACTION_INSTRUCTION = """You are an information extraction system. The input is the markdown content of a web page.

Your job:
1. Read the page and identify ONLY the main content. Ignore site navigation, headers, footers,
   sidebars, related-article lists, comment sections, cookie banners, ads, and "subscribe" prompts.
2. Extract data that exactly matches the JSON schema provided in the response_format.
3. If a field cannot be found in the main content, leave it empty (empty string for text,
   empty list for arrays, null for optional numbers). Never invent values.
4. Preserve original text faithfully — do not paraphrase unless the schema asks for a summary.

Return ONLY valid JSON matching the schema. No prose, no markdown, no explanations.
"""


# ---------- Scientific paper extraction (Phase 2) ----------

SCIENTIFIC_PAPER_INSTRUCTION = """You are extracting structured metadata from the markdown of a scientific paper page
(could be arXiv, PubMed Central, a publisher landing page, an institutional repository, or a preprint server).

Layouts vary wildly across these sites. Focus on semantic content, not visual structure.

EXTRACT:
- title: Full paper title as stated on the page.
- authors: List of authors. For each, extract name; if affiliation or ORCID is visible, include it.
- abstract: The paper's abstract. If the page has an explicit "Abstract" section, use that.
  If not, write a 3-4 sentence faithful summary of the paper's stated topic and contribution
  based ONLY on text present on the page. Never fabricate.
- methodology: 2-4 sentences describing the core method, dataset, model, or experimental setup.
  Answer "what did they DO?" Avoid restating the abstract. If methodology details are not
  on the page (e.g., abstract-only landing page), leave empty.
- conclusions: 2-4 sentences on findings and stated implications. Answer "what did they CONCLUDE?"
  If not on the page, leave empty.
- keywords: 3-8 lowercase keywords. Prefer concrete techniques and concepts (e.g.
  "transformer", "knowledge graph", "few-shot learning") over generic words ("paper", "study").
  If the page lists keywords explicitly, use those.
- publication_year: Integer year if visible. Else null.
- venue: Journal or conference name if visible. Else null.
- doi: DOI string if visible. Else null.
- image_url: A single representative image URL — paper figure thumbnail or first
  scientific figure if any. NOT site logos, NOT author photos, NOT ad/banner images.
  Empty string if none.

NOISE TO IGNORE:
- "Cite this paper", "Download PDF", "Subscribe", login prompts, navigation menus, related links.
- Recommendations sidebars ("You might also like").
- Cookie banners and GDPR notices.
- Author-bio side blocks unrelated to the paper.

If the page is a paywall or login wall (you see "Sign in to read", "Purchase access", "Login required",
"This article is behind a paywall", etc.) and no abstract is visible, return all fields empty.

Return ONLY valid JSON. No prose."""


# ---------- Relevance filter ----------

RELEVANCE_FILTER_INSTRUCTION = """You are a strict relevance scorer for a scientific literature search.

Given a research topic and a list of candidate papers (each with a title and short abstract),
score each paper from 0.0 to 1.0 by how directly its CONTENT addresses the topic:

- 1.0 = paper is centrally about the topic — main contribution is on this exact subject
- 0.7 = topic is one of the paper's main themes
- 0.4 = topic is a supporting concept used by the paper but not its focus
- 0.1 = paper only mentions the topic incidentally, or shares a keyword but addresses
        a different subject
- 0.0 = irrelevant, off-topic, OR a non-paper artifact (dataset dump, AI-generated junk,
        explicit "for entertainment only" disclaimers, blog post, software changelog)

STRICT RULES — these MUST score ≤ 0.1, regardless of word overlap:
- Papers whose abstract contains "AI for entertainment", "written purely by AI",
  "not intended for peer review", "not peer reviewed", "for fun" — these are junk.
- Papers whose topic only matches by sharing a NAME (e.g. searching "Gemini in
  Programming" and matching a paper about the Gemini space program, the constellation,
  or a person named Gemini) — these are NOT topical matches.
- Empty or near-empty abstracts (<50 chars) when the title is generic — score ≤ 0.2.

Match by CONTENT and INTENT, not by string overlap. A paper titled
"Mathematical derivation of physics by Google Gemini" is NOT relevant to
"Gemini in Programming" — different domain entirely.

Return ONLY valid JSON: an object {"scores": [{"id": int, "score": float}, ...]}.
Include every paper's id exactly once. Do not invent ids."""


# ---------- Translation (post-extraction) ----------

# ---------- Benchmark default — works on papers AND news/blog/etc. ----------

BENCHMARK_DEFAULT_INSTRUCTION = """Extract structured metadata from the markdown of this web page.

Read the page and identify ONLY the main content (headline + body). Ignore site
navigation, headers, footers, sidebars, related-article lists, ads, comment sections,
cookie banners, and "subscribe" prompts.

EXTRACT:
- title: The main headline / page title.
- authors: Array of author names. Empty array if none stated.
- abstract: A 2-4 sentence faithful summary of the main content. For papers, use the
  paper's abstract verbatim if one is shown. For news/blog posts, summarise the body.
- methodology: 2-3 sentences on method/approach IF this is a scientific paper.
  Otherwise empty string.
- conclusions: 2-3 sentences on findings/conclusions IF this is a scientific paper.
  Otherwise empty string.
- keywords: 3-8 lowercase tags or topic keywords. If the page lists keywords/tags
  explicitly, use those. Else infer from content.
- publication_year: Integer year if visible, else null.
- venue: Journal/conference name for papers, or publication/site name for news/blog.
- doi: DOI string if visible, else null.
- image_url: One representative image URL from the main content (lead photo for
  news, figure for papers, hero image for blog). NOT site logo, NOT author photo,
  NOT ads/banners, NOT thumbnails of related articles. Empty string if none.

Return ONLY valid json matching this shape. No prose, no markdown wrappers."""


TRANSLATION_INSTRUCTION_TEMPLATE = """Translate the following text fields to {target_lang}.
Preserve technical terms (model names, algorithm names, dataset names) untranslated.
Do not paraphrase — translate faithfully. Preserve newlines and structure.

Return ONLY valid JSON with the same keys, values translated."""
