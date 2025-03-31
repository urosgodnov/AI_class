

import xml.etree.ElementTree as ET
from typing import List
from urllib.parse import urljoin
from docling.document_converter import DocumentConverter
import requests


        # Extract URLs using namespace if present
root="""
<url>
<loc>https://www.grasca.si/turne-in-freeride-smuci</loc>
<lastmod>2025-03-31</lastmod>
<changefreq>daily</changefreq>
<priority>0.9</priority>
</url>
<url>
<loc>https://www.grasca.si/all-mountain-smuci</loc>
<lastmod>2025-03-31</lastmod>
<changefreq>daily</changefreq>
<priority>0.9</priority>
</url>
"""        
        

urls = ["https://www.grasca.si/gorsko-kolo-scott-spark-920-23",
        "https://www.grasca.si/gorsko-kolo-scott-spark-930-or-22-s",
        "https://www.grasca.si/kolesa/cestno-kolo-scott-addict-rc-30-cr-25"]

        
converter = DocumentConverter()

conv_results_iter = converter.convert_all(urls)

docs = []
for result in conv_results_iter:
    if result.document:
        document = result.document
        markdown_output = document.export_to_markdown()
        docs.append(markdown_output)
