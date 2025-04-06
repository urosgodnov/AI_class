# when go line by line, the code is not working
# use pip black and then reformat the code

from typing import List

import lancedb
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from openai import OpenAI
from tokenizer_custom import OpenAITokenizerWrapper

"""
LanceDB is a fast, local, and scalable vector database built on top of Apache Arrow. 
It’s designed for storing and searching embeddings (like those from LLMs) efficiently. 
It uses Lance, a columnar storage format optimized for machine learning workloads.

You can think of LanceModel like a database schema that includes both text and vector fields.
"""

load_dotenv()

tokenizer = OpenAITokenizerWrapper()
MAX_TOKENS = 8191

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = False
pipeline_options.table_structure_options.do_cell_matching = False

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend
        )
    }
)

converter = DocumentConverter()
result = doc_converter.convert("https://arxiv.org/pdf/2408.09869")

chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=MAX_TOKENS,
    merge_peers=True,
)

chunk_iter = chunker.chunk(dl_doc=result.document)
chunks = list(chunk_iter)

# --------------------------------------------------------------
# Create a LanceDB database and table
# --------------------------------------------------------------

# Create a LanceDB database
db = lancedb.connect("data/lancedb")


func = get_registry().get("openai").create(name="text-embedding-3-small")


# Define the metadata schema

class ChunkMetadata(LanceModel):
    # You must order the fields in alphabetical order.
    # This is a requirement of the Pydantic implementation.
    filename: str | None
    page_numbers: List[int] | None
    title: str | None


# Define the main Schema

class Chunks(LanceModel):
    text: str = func.SourceField()
    vector: Vector(func.ndims()) = func.VectorField()  # type: ignore
    metadata: ChunkMetadata


table = db.create_table("docling", schema=Chunks, mode="overwrite")

# --------------------------------------------------------------
# Prepare the chunks for the table
"""
This list comprehension creates a list of dictionaries, each representing a processed text 
chunk along with its metadata.
"""
# --------------------------------------------------------------

# Create table with processed chunks
processed_chunks = [
    {
        "text": chunk.text,
        "metadata": {
            "filename": chunk.meta.origin.filename,
            "page_numbers": [
                page_no
                for page_no in sorted(
                    set(
                        prov.page_no
                        for item in chunk.meta.doc_items
                        for prov in item.prov
                    )
                )
            ]
            or None,
            "title": chunk.meta.headings[0] if chunk.meta.headings else None,
        },
    }
    for chunk in chunks
]

# --------------------------------------------------------------
# Add the chunks to the table (automatically embeds the text)
# --------------------------------------------------------------

table.add(processed_chunks)

# --------------------------------------------------------------
# Load the table
# --------------------------------------------------------------

table.to_pandas()
table.count_rows()


