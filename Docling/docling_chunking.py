"""
Chunking is the process of splitting a long document into smaller pieces ("chunks") 
so that it fits within the context window limitations of a given Large Language Model 
(LLM). Essentially, if you have a large text, you want to ensure that the LLM doesn’t 
exceed its token capacity.
"""
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.document_converter import DocumentConverter, PdfFormatOption
from dotenv import load_dotenv
from openai import OpenAI
from Docling.tokenizer_custom import OpenAITokenizerWrapper

load_dotenv()
"""
Tokens are the fundamental units a language model uses to process text. 
A token might be a word, a part of a word, or even special characters. 
For example, in English, many common words are a single token, 
while some longer or less common words may be split into multiple tokens. 
Punctuation and special symbols can each be counted as their own token.    
n practice, one token often corresponds to roughly 0.75 to 1 word in English, 
depending on the tokenizer and text style. This means 8191 tokens can range from around 
6,000 to 8,000 words.
"""

tokenizer = OpenAITokenizerWrapper()  # Load our custom tokenizer for OpenAI
MAX_TOKENS = 8191

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = False
pipeline_options.table_structure_options.do_cell_matching = False

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend)
    }
)

converter = DocumentConverter()
result = doc_converter.convert("https://arxiv.org/pdf/2408.09869")
                               
                              
# Apply hybrid chunking
# --------------------------------------------------------------
"""
Semantic or Structural Boundaries: Instead of blindly chopping text at arbitrary points, 
a hybrid chunker tries to respect boundaries such as paragraphs, headings, or sections. 
This prevents chunk splits in the middle of a sentence or formula, 
which can make the text less coherent for a language model.
"""


chunker = HybridChunker(
    tokenizer=tokenizer,
    max_tokens=MAX_TOKENS,
    merge_peers=True,
)

chunk_iter = chunker.chunk(dl_doc=result.document)
chunks = list(chunk_iter)

len(chunks)