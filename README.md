# EIDOS-NewsCrawler
A fully autonomous news &amp; trend crawler built by the EIDOS framework.  Collects articles, extracts key insights, and generates daily summaries.


-EIDOS News Scout

A lightweight crawler that collects news articles and trending topics from multiple sources and generates concise summaries.

This tool was created in just five minutes through an automated workflow in EIDOS, a framework I’ve been developing for building self-improving software systems.
Although the implementation was generated quickly, the structure is intentionally simple, readable, and easy to extend.



<Features>

Multi-source crawling
Crawls news sites or trend pages (RSS or HTML) depending on configuration.

Automatic content extraction
Removes ads, boilerplate text, and extracts only the main article section.

Keyword & topic detection
Identifies the core topics from each article using lightweight techniques.

Short summary generation
Produces clear and compact summaries for quick review.

Daily digest mode
Generates a consolidated summary of all crawled content for the day.

Configurable pipeline
URLs, depth, summary length, and output format can all be changed easily.




<Usage>
# Install dependencies
pip install -r requirements.txt

# Run the crawler
python src/crawler.py


Configuration can be updated in config.py depending on the target news sources or desired summary length.





<Goal of This Tool>

This repository isn’t meant to be a large-scale production crawler.
It’s meant to demonstrate how a simple, working tool can be produced rapidly through iterative software workflows.

EIDOS handled:

pipeline design

scaffolding

implementation

cleanup

formatting

My role was simply verifying the logic and running the final script.




<Notes>

This project will continue to evolve as EIDOS gains new capabilities.

Contributions, suggestions, and improvements are welcome
