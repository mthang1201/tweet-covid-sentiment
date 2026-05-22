import pandas as pd
import argparse
import time
import os

def process_large_dataset(input_file: str, output_file: str, chunksize: int = 100000, delimiter: str = ','):
    """
    Process a large dataset in chunks to avoid OOM errors.
    
    Args:
        input_file (str): Path to the input large dataset file.
        output_file (str): Path to the output processed dataset file.
        chunksize (int): Number of rows to read per chunk. Default is 100,000.
        delimiter (str): Delimiter used in the file (e.g., ',' for CSV, '\t' for TSV). Default is ','.
    """
    print(f"Starting to process '{input_file}'...")
    print(f"Parameters: chunksize={chunksize}, delimiter='{delimiter}'")
    
    start_time = time.time()
    
    # Optional: ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    try:
        # Create a reader object
        reader = pd.read_csv(
            input_file,
            chunksize=chunksize,
            sep=delimiter,
            on_bad_lines='skip',
            low_memory=False # Helps with mixed types if present
        )
        
        for i, chunk in enumerate(reader):
            chunk_start_time = time.time()
            print(f"Processing chunk {i + 1}...")
            
            # ------------------------------------------------------------------
            # CUSTOM LOGIC GOES HERE
            # ------------------------------------------------------------------
            # Example operations you might perform on 'chunk' (which is a DataFrame):
            # 
            # 1. Drop irrelevant columns:
            # columns_to_drop = ['col1', 'col2']
            # chunk.drop(columns=[col for col in columns_to_drop if col in chunk.columns], inplace=True)
            #
            # 2. Filter rows by specific conditions:
            # chunk = chunk[chunk['status'] == 'active']
            #
            # 3. Handle missing values:
            # chunk.fillna({'age': 0}, inplace=True)
            # chunk.dropna(subset=['id'], inplace=True)
            #
            # 4. Data transformations:
            # chunk['date'] = pd.to_datetime(chunk['date'])
            # ------------------------------------------------------------------
            
            # Determine how to write the chunk
            # The first chunk must create the file and write the header (mode='w', header=True)
            # Subsequent chunks append to the file without the header (mode='a', header=False)
            write_mode = 'w' if i == 0 else 'a'
            write_header = True if i == 0 else False
            
            chunk.to_csv(
                output_file,
                index=False,
                mode=write_mode,
                header=write_header,
                sep=delimiter
            )
            
            chunk_time = time.time() - chunk_start_time
            print(f"  -> Chunk {i + 1} processed and saved in {chunk_time:.2f} seconds.")
            
        total_time = time.time() - start_time
        print(f"Successfully finished processing '{input_file}'.")
        print(f"Total time elapsed: {total_time:.2f} seconds.")
        print(f"Output saved to '{output_file}'.")
        
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a large dataset in chunks.")
    parser.add_argument(
        "-i", "--input", 
        required=True, 
        help="Path to the input large dataset file (e.g., data/large_file.csv)"
    )
    parser.add_argument(
        "-o", "--output", 
        required=True, 
        help="Path to the output processed file (e.g., data/processed_file.csv)"
    )
    parser.add_argument(
        "-c", "--chunksize", 
        type=int, 
        default=100000, 
        help="Number of rows per chunk (default: 100000)"
    )
    parser.add_argument(
        "-d", "--delimiter", 
        type=str, 
        default=",", 
        help="Delimiter used in the dataset. Use ',' for CSV or '\\t' for TSV. (default: ',')"
    )
    
    args = parser.parse_args()
    
    # Handle literal \t from command line if user passes it as a string
    delimiter = '\t' if args.delimiter == '\\t' else args.delimiter
    
    process_large_dataset(
        input_file=args.input,
        output_file=args.output,
        chunksize=args.chunksize,
        delimiter=delimiter
    )
