# News & Trend Summary Crawler

Automatically collects news articles and generates concise summaries.
(This project was drafted end-to-end in under 5 minutes using an early prototype of my EIDOS system.)



<Overview>

This repository contains a simple automation tool that collects news articles from multiple sources, extracts their content, and uses an LLM to generate:

Summaries

Keywords

Basic topic classification

It’s not meant to be a polished, production-ready framework —
rather, it was created as a quick experimental test for the EIDOS architecture.
You can easily extend it to additional websites or formats.



<Features>

Asynchronous crawling using aiohttp
Article parsing with BeautifulSoup
LLM-powered processing
Article summarization
Keyword extraction
Category classification
Duplicate filtering (title & URL)
Modular code structure, easy to modify or expand




< Requirements>
Python 3.10+
Install dependencies:
aiohttp
beautifulsoup4
openai>=1.0.0



<OpenAI API Key>

This project requires an OpenAI API key for the LLM functions.
Set it as an environment variable:

macOS/Linux
export OPENAI_API_KEY="YOUR_KEY_HERE"

Windows PowerShell
setx OPENAI_API_KEY "YOUR_KEY_HERE"




<Notes>
The CSS selectors used for scraping are minimal and may need adjustment depending on the news source.
The crawler includes only a few demo sites — feel free to add your own.
Since this was created quickly as part of an internal EIDOS experiment, you may want to refactor or extend it for long-term use.
