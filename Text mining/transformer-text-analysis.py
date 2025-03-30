import pandas as pd
from transformers import pipeline
from joblib import Parallel, delayed
import math
from tqdm import tqdm

#############################
# In this script, we use "distilbert/distilbert-base-uncased-finetuned-sst-2-english" from Hugging Face.
# DistilBERT is a lightweight, distilled version of BERT, fine-tuned for sentiment analysis (SST-2 dataset),
# making it faster and smaller than the original BERT while retaining a comparable level of accuracy.
#
# BERT was originally implemented in the English language at two model sizes, 
# BERTBASE (110 million parameters) and BERTLARGE (340 million parameters). 
# Both were trained on the Toronto BookCorpus[6] (800M words) and English Wikipedia (2,500M words)
# We utilize the 'pipeline' API from the transformers library to simplify inference, automatically handling
# tokenization, model forwarding, and output formatting. Specifically, we use the 'sentiment-analysis' pipeline,
# which interprets text and classifies it as 'POSITIVE' or 'NEGATIVE'. We then transform these labels into
# continuous scores in the [-1, 1] range.
#
# For large datasets, running inference sequentially can be slow, hence we use joblib's Parallel and delayed
# functions. This splits the DataFrame into roughly equal-sized slices and processes them concurrently. Each
# process initializes its own model instance (to avoid concurrency conflicts within a single model object),
# and each slice is handled in parallel, improving overall throughput on systems with multiple CPU cores.
#############################


# Convert sentiment labels to continuous scores in [-1, 1]
def convert_to_minus_one_to_one(label: str, score: float) -> float:
    if label.upper() == "POSITIVE":
        return score
    else:
        return -score

# Process a slice of data with sentiment analysis pipeline
def process_slice(df_slice: pd.DataFrame, slice_id: int) -> pd.DataFrame:
    #############################
    # We create a new sentiment-analysis pipeline inside this function for each slice.
    # This ensures that each parallel process has its own pipeline instance, preventing
    # potential collisions when the same model is shared across processes.
    #############################

    sentiment_model = pipeline(
        "sentiment-analysis",
        model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512
    )

    texts = df_slice["fullrev"].tolist()

    polarity_list, score_list, confidence_list = [], [], []

    batch_size = 8
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        try:
            #############################
            # We process smaller batches of text (batch_size=8) to manage memory usage,
            # especially when dealing with very large DataFrames.
            #############################
            results = sentiment_model(batch_texts)

            for r in results:
                label = r["label"]
                raw_score = r["score"]
                sentiment_value = convert_to_minus_one_to_one(label, raw_score)
                polarity_list.append(label)
                score_list.append(sentiment_value)
                confidence_list.append(abs(sentiment_value))
        except Exception as e:
            print(f"Error in slice {slice_id}, batch {i//batch_size}: {str(e)}")
            polarity_list.extend(["NEUTRAL"] * len(batch_texts))
            score_list.extend([0.0] * len(batch_texts))
            confidence_list.extend([0.0] * len(batch_texts))

    out_df = df_slice.copy()
    out_df["transformer_polarity"] = polarity_list
    out_df["transformer_score"] = score_list
    out_df["transformer_confidence"] = confidence_list

    print(f"Completed processing slice {slice_id}")
    return out_df

# Chunk DataFrame into smaller slices
def chunk_df(df: pd.DataFrame, n_chunks: int):
    #############################
    # chunk_df yields consecutive slices of the original DataFrame so that each
    # slice can be processed separately in parallel.
    #############################
    chunk_size = math.ceil(len(df) / n_chunks)
    for i in range(n_chunks):
        start = i * chunk_size
        end = start + chunk_size
        yield df.iloc[start:end]

# Main function orchestrating the parallel sentiment analysis
def main():
    #############################
    # We load the dataset, specify the number of parallel jobs, split the data into slices,
    # then process each slice concurrently. The partial results are concatenated into a single
    # DataFrame and saved as an Excel file.
    #############################

    df = pd.read_excel("tripadvisor.xlsx", sheet_name=0)

    n_jobs = 8  # Number of workers to parallelize over.
    slices = list(chunk_df(df, n_jobs))

    processed_slices = Parallel(n_jobs=n_jobs)(
        delayed(process_slice)(df_slice, i)
        for i, df_slice in enumerate(slices)
    )

    result_df = pd.concat(processed_slices).sort_index()
    result_df.to_excel("tripadvisor_with_transformer_sentiment.xlsx", index=False)
    print("Processing complete and results saved.")

if __name__ == "__main__":
    main()
