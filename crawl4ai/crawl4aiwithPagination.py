import asyncio
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
import json

async def css_extraction():
    schema = {
        "name": "Quotes",
        "baseSelector": "div.quote",
        "fields": [
            {"name": "quote", "selector": "span.text", "type": "text"},
            {"name": "author", "selector": "small.author", "type": "text"}
        ]
    }

    results_folder = os.path.join(os.getcwd(), "crawl_results")
    os.makedirs(results_folder, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extraction_strategy = JsonCssExtractionStrategy(schema)
    session_id = f"session_{timestamp}"

    all_quotes = []  # Collect all quotes here
    
    url = "http://quotes.toscrape.com/"

    async with AsyncWebCrawler() as crawler:
        for page in range(5):  # Crawl 4 pages
            run_config = CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                verbose=True,
                session_id=session_id,
                js_code=[
                    "document.querySelector('ul.pager li.next a')?.click();"
                ] if page > 0 else None,
                js_only=page > 0            )

            result = await crawler.arun(url=url, config=run_config)

            if result.success:
                quotes_data = json.loads(result.extracted_content)
                all_quotes.extend(quotes_data) 
                
                print(f"Extracted from page {page + 1}:")

                #markdown_path = os.path.join(results_folder, f"crawl_result_{timestamp}_page_{page + 1}.md")

                #with open(markdown_path, "w", encoding="utf-8") as f:
                #    f.write(result.markdown)
            else:
                print(f"Extraction Error on page {page + 1}:", result.error_message)

        json_filename = os.path.join(results_folder, f"quotes_{timestamp}.json")
        with open(json_filename, "w", encoding="utf-8") as json_file:
            json.dump(all_quotes, json_file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(css_extraction())
