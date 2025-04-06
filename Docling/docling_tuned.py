import pandas as pd
import time
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.backend.docling_parse_v2_backend import DoclingParseV2DocumentBackend
from docling.document_converter import DocumentConverter, PdfFormatOption
import os
# Disable ALL potentially problematic models
# os.environ["DOCLING_DISABLE_LAYOUT_MODEL"] = "1"
# os.environ["DOCLING_DISABLE_OCR"] = "1"
# os.environ["DOCLING_DISABLE_TABLE_STRUCTURE"] = "1"
# os.environ["DOCLING_DISABLE_PICTURE_CLASSIFICATION"] = "1"
# os.environ["DOCLING_DISABLE_PICTURE_DESCRIPTION"] = "1"
# os.environ["DOCLING_DISABLE_CODE_ENRICHMENT"] = "1"
# os.environ["DOCLING_DISABLE_FORMULA_ENRICHMENT"] = "1"

# docling is slow
# what can we do to speed it up?

# parallelize the requests
# Turn off OCR if you don't need it for your data (e.g. you bring digital-only PDFs)
# CLI option --no-ocr
# Turn off table structure recognition if you don't need table structure (e.g. your PDFs have no tables or you don't need the table's content)
# only possible in python API code, see below.
# Switch the PDF backend to DoclingParseV2DocumentBackend, which speeds up PDF loading by ~10x, with good impact on the overall pipeline speed.
# CLI arg  --pdf-backend= dlparse_v2

file_path = "https://arxiv.org/pdf/2408.09869"

results = []

# Option 1: Basic conversion
start = time.time()
result = DocumentConverter().convert(file_path)
option1_time = time.time() - start
results.append({
    "Option": "Option 1: Default configuration",
    "Description": "Uses default DocumentConverter() with no customization",
    "Execution Time (s)": option1_time
})
print(f"Option number 1: {option1_time}")

# Option 2: Full features with explicit configuration
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.do_cell_matching = True

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend)
    }
)

start = time.time()
result = doc_converter.convert(file_path)
option2_time = time.time() - start
results.append({
    "Option": "Option 2: Full features with explicit configuration",
    "Description": "Enables OCR, table structure analysis, and cell matching",
    "Execution Time (s)": option2_time
})
print(f"Option number 2: {option2_time}")

# Option 3: Basic optimization
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = False
pipeline_options.table_structure_options.do_cell_matching = False

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options, backend=PyPdfiumDocumentBackend)
    }
)

start = time.time()
result = doc_converter.convert(file_path)
option3_time = time.time() - start
results.append({
    "Option": "Option 3: Basic optimization",
    "Description": "Disables OCR, table structure analysis, and cell matching",
    "Execution Time (s)": option3_time
})
print(f"Option number 3: {option3_time}")



# Option 4: Maximum optimization
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = False
pipeline_options.table_structure_options.do_cell_matching = False
pipeline_options.accelerator_options.num_threads = 2
pipeline_options.generate_page_images = False
pipeline_options.generate_picture_images = False
pipeline_options.do_code_enrichment = False
pipeline_options.do_formula_enrichment = False
pipeline_options.generate_table_images = False
pipeline_options.generate_parsed_pages = False
pipeline_options.document_timeout = 60

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options, 
            backend=PyPdfiumDocumentBackend
        )
    }
)

start = time.time()
result = doc_converter.convert(file_path)
option4_time = time.time() - start
results.append({
    "Option": "Option 4: Maximum optimization",
    "Description": "Disables all extra features and reduces thread count to 2",
    "Execution Time (s)": option4_time
})
print(f"Option number 4: {option4_time}")

# option 5
# DoclingParseV2DocumentBackend it should be 10 times faster
"""
Key features:

Faster PDF Loading: According to the comment in your code, it speeds up PDF loading by approximately 10x compared to the standard backend.
Performance-Oriented: It's designed specifically for scenarios where processing speed is the primary concern.
"""
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False
pipeline_options.do_table_structure = False
pipeline_options.table_structure_options.do_cell_matching = False
pipeline_options.accelerator_options.num_threads = 2
pipeline_options.generate_page_images = False
pipeline_options.generate_picture_images = False
pipeline_options.do_code_enrichment = False
pipeline_options.do_formula_enrichment = False
pipeline_options.generate_table_images = False
pipeline_options.generate_parsed_pages = False
pipeline_options.document_timeout = 60


doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options, 
            backend=DoclingParseV2DocumentBackend
        )
    }
)

start = time.time()
result = doc_converter.convert(file_path)
option5_time = time.time() - start
results.append({
    "Option": "Option 5: DoclingParseV2 backend",
    "Description": "Uses DoclingParseV2DocumentBackend with basic optimizations",
    "Execution Time (s)": option5_time
})
print(f"Option number 5: {option5_time}")

df = pd.DataFrame(results)

# Calculate speedup compared to Option 1 (baseline)
baseline_time = df.loc[0, "Execution Time (s)"]
df["Speedup (x)"] = baseline_time / df["Execution Time (s)"]

print("\nSpeedup Comparison:")
print(df[["Option", "Description", "Execution Time (s)", "Speedup (x)"]])

df.to_excel("docling_speedup_comparison.xlsx", index=False)