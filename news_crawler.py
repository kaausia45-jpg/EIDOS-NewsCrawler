import asyncio
import logging
from typing import List, Dict, Any
import aiohttp
from bs4 import BeautifulSoup

# NOTE: CSS selectors are placeholders and must be adapted for each target website.
# This is a simplified example.
SITE_CONFIG = {
    'https://news.naver.com/': {
        'article_link_selector': 'a.sa_item_title'
    },
    'https://www.etnews.com/': {
        'article_link_selector': 'a.list_news'
    }
}

class NewsCrawler:
    def __init__(self):
        self.processed_urls = set()

    async def fetch_page(self, session: aiohttp.ClientSession, url: str) -> str | None:
        try:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                response.raise_for_status()
                return await response.text()
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def parse_article(self, html: str, url: str) -> Dict[str, Any] | None:
        # This is a placeholder parsing logic. Real implementation needs specific selectors for each site.
        try:
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find('h1') or soup.find('h2') or soup.find('h3')
            content_body = soup.find('article') or soup.find('div', id='articleBodyContents') or soup.find('div', class_='article_body')
            
            if not title or not content_body:
                logging.warning(f"Could not parse title/content for {url}")
                return None

            title_text = title.get_text(strip=True)
            content_text = '\n'.join(p.get_text(strip=True) for p in content_body.find_all('p'))

            return {
                'title': title_text,
                'content': content_text,
                'url': url
            }
        except Exception as e:
            logging.error(f"Error parsing article at {url}: {e}")
            return None

    async def process_article_url(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any] | None:
        if url in self.processed_urls:
            return None
        html = await self.fetch_page(session, url)
        if html:
            article = self.parse_article(html, url)
            if article:
                self.processed_urls.add(url)
                return article
        return None

    async def crawl_site(self, session: aiohttp.ClientSession, site_url: str, config: Dict) -> List[Dict[str, Any]]:
        logging.info(f"Crawling main page: {site_url}")
        main_html = await self.fetch_page(session, site_url)
        if not main_html:
            return []

        soup = BeautifulSoup(main_html, 'html.parser')
        article_links = set()
        for link in soup.select(config['article_link_selector']):
            href = link.get('href')
            if href and href.startswith('http'):
                article_links.add(href)
            elif href:
                from urllib.parse import urljoin
                article_links.add(urljoin(site_url, href))

        if not article_links:
            logging.warning(f"No article links found on {site_url} with selector '{config['article_link_selector']}'")
            return []
        
        logging.info(f"Found {len(article_links)} article links. Processing in parallel...")
        
        tasks = [self.process_article_url(session, url) for url in article_links]
        results = await asyncio.gather(*tasks)
        
        return [article for article in results if article]

    async def crawl(self) -> List[Dict[str, Any]]:
        all_articles = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.crawl_site(session, site, config) for site, config in SITE_CONFIG.items()]
            site_results = await asyncio.gather(*tasks)
            for result in site_results:
                all_articles.extend(result)
        
        # Simple duplication check based on title
        unique_articles = {article['title']: article for article in all_articles}.values()
        logging.info(f"Crawling finished. Found {len(unique_articles)} unique articles.")
        return list(unique_articles)
