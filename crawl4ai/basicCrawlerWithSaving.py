# Example 2: Saving the results to a file

# Import necessary libraries
import asyncio  # For async/await functionality
import os  # For file and directory operations
from datetime import datetime  # For generating timestamps
from crawl4ai import AsyncWebCrawler
import json  # For JSON handling

async def basic_crawl():
    """
    Asynchronous function that crawls a website and saves the result.
    - Creates a folder for storing results
    - Crawls quotes.toscrape.com
    - Saves the markdown output to a timestamped file
    """
    # Create results folder if it doesn't exist
    results_folder = os.path.join(os.getcwd(), "crawl_results")
    os.makedirs(results_folder, exist_ok=True)
    
    # Generate timestamp for unique filename (format: YYYYMMDD_HHMMSS)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Use AsyncWebCrawler as a context manager
    async with AsyncWebCrawler() as crawler:
        # Start the crawling process with the target URL
        result = await crawler.arun(url="http://quotes.toscrape.com/")
        
        # Check if crawling was successful
        if result.success:
            # Print a preview of the markdown (first 500 characters)
            print("Markdown preview:\n", result.markdown[:500])
            
            # Create the full path for saving the markdown file
            markdown_path = os.path.join(results_folder, f"crawl_result_{timestamp}.md")
            
            # Write the markdown content to the file
            with open(markdown_path, "w", encoding="utf-8") as f:
                f.write(result.markdown)
            
            # Print confirmation message with the file path
            print(f"Crawl result saved to: {markdown_path}")
        else:
            # Print error message if crawling failed
            print("Error:", result.error_message)

# Entry point of the script
if __name__ == "__main__":
    # Run the async function using asyncio
    asyncio.run(basic_crawl())