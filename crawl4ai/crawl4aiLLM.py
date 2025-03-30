import asyncio
import json
import os
from datetime import datetime
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv


api_key = os.getenv("OPENAI_API_KEY")
#api_key = "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"
model_name = "openai/gpt-4o-mini"


url="https://www.imdb.com/title/tt6208148/reviews/?ref_=tt_ururv_sm"
all_reviews = []
session_id = "movie_reviews_session"
results_folder = os.path.join(os.getcwd(), "crawl_results_imdb_llm")
os.makedirs(results_folder, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

js_click_all = "document.querySelector('span.chained-see-more-button button.ipc-see-more__button')?.click();"

class ReviewsResult(BaseModel):
    author:str 
    rating:str
    review_text:str



async def main():
    llm_strategy = LLMExtractionStrategy(
        llm_config = LLMConfig(provider=model_name, api_token=api_key),
        schema=ReviewsResult.model_json_schema(), 
        extraction_type="schema",
        instruction="""
        Focus on extracting the reviews from the provided HTML content.
        Include:
        - Author name: please dont generate your own authors names. If you cant find the
        author, leave it.
        - Ratings: rating should be between 1 and 10
        - Review text: please dont generate your own review text. If you cant find the review, leave it.
        Example:
        "author": "John Doe",
        "rating": "8",
        "review_text": "This movie was fantastic! I loved the plot and the characters."

        """,
        input_format="html"
    )

    run_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        verbose=True,
        keep_attrs=["article"],
        keep_data_attributes=True,
        #js_code=js_click_all,
        delay_before_return_html=10,
        session_id=session_id)

    async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                config=run_config
            )
            if result.success:
                reviews_data = json.loads(result.extracted_content)
                filtered_reviews = [review for review in reviews_data if review.get("author")]
                unique_reviews_by_author = {}
                for review in filtered_reviews:
                    author = review["author"]

                    if author not in unique_reviews_by_author:
                        unique_reviews_by_author[author] = review
                
                distinct_reviews = list(unique_reviews_by_author.values())
                all_reviews.extend(distinct_reviews)
            else:
                print("I have no idea why it doesnt work!")

    
    json_filename = os.path.join(results_folder, f"imdb_reviews_all_{timestamp}.json")
    if all_reviews:
        try:
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(all_reviews, json_file, ensure_ascii=False, indent=4)
            print(f"Successfully saved {len(all_reviews)} reviews to {json_filename}") # Minimal output
        except Exception as e:
            print(f"Error: Failed to save reviews to JSON file: {e}", file=sys.stderr)
    else:
         print("Warning: No reviews were collected. Skipping JSON file creation.", file=sys.stderr)               

if __name__ == "__main__":
    asyncio.run(main())
