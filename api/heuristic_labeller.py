import pandas as pd
import numpy as np
import os

def assign_labels(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns semantic labels (title, h1, h2, h3, paragraph, list_item) to text lines
    based on their formatting and positional metadata.

    Args:
        df (pd.DataFrame): A DataFrame containing text metadata for a single PDF.

    Returns:
        pd.DataFrame: The DataFrame with an added 'label' column.
    """
    
    # --- Initial Setup ---
    # Initialize the label column with a default value
    df['label'] = 'paragraph'
    
    # Calculate the most common (mode) font size, likely the main paragraph font size
    try:
        paragraph_font_size = df['font_size'].mode()[0]
    except IndexError:
        paragraph_font_size = 12.0 # A reasonable default

    # --- Rule 1: List Items ---
    # List items are primarily identified by a bullet character.
    df.loc[df['bullet_char'] == True, 'label'] = 'list_item'

    # --- Rule 2: Title ---
    # The title is usually unique, on the first page, has the largest font, and is near the top.
    # We filter out list items and very short text to avoid mislabeling.
    non_list_items = df[df['label'] != 'list_item'].copy()
    non_list_items = non_list_items[non_list_items['text_length'] > 2]

    if not non_list_items.empty:
        first_page_df = non_list_items[non_list_items['is_first_page'] == True]
        if not first_page_df.empty:
            # A good title candidate has the largest font size on the first page.
            # Using font_size_rank is a great shortcut if available.
            title_font_size = first_page_df['font_size'].max()
            title_candidates = first_page_df[first_page_df['font_size'] == title_font_size]
            
            if not title_candidates.empty:
                # Of the candidates, the one highest on the page (lowest y0) is the title.
                title_index = title_candidates['y0'].idxmin()
                df.loc[title_index, 'label'] = 'title'

    # --- Rule 3: Headings (h1, h2, h3) ---
    # Headings are identified by a combination of features: boldness, font size,
    # text length, and capitalization.
    
    # Candidates for headings are non-list, non-title, and non-paragraph-like lines.
    heading_candidates = df[(df['label'] != 'list_item') & (df['label'] != 'title')].copy()
    
    # A strong signal for a heading is being bold and having a font size
    # larger than the main body text.
    potential_headings = heading_candidates[
        (heading_candidates['bold_ratio'] >= 0.8) & 
        (heading_candidates['font_size'] > paragraph_font_size)
    ]

    # Another strong signal is ending with a colon or having a high ratio of capitalized words.
    potential_headings_style = heading_candidates[
        (heading_candidates['ends_with_colon'] == True) |
        (heading_candidates['capitalized_words_ratio'] > 0.5) &
        (heading_candidates['num_words'] < 10) # Headings are usually short
    ]

    # Combine the candidates
    bold_texts = pd.concat([potential_headings, potential_headings_style]).drop_duplicates()

    if not bold_texts.empty:
        # Get unique font sizes of our heading candidates and sort them descending.
        # This hierarchy will determine h1, h2, h3.
        heading_font_sizes = sorted(bold_texts['font_size'].unique(), reverse=True)
        
        # Map the top 3 font sizes to heading levels
        heading_levels = {}
        if len(heading_font_sizes) > 0:
            heading_levels[heading_font_sizes[0]] = 'h1'
        if len(heading_font_sizes) > 1:
            heading_levels[heading_font_sizes[1]] = 'h2'
        if len(heading_font_sizes) > 2:
            heading_levels[heading_font_sizes[2]] = 'h3'

        # Apply heading labels based on font size
        for size, level in heading_levels.items():
            indices_to_label = bold_texts[bold_texts['font_size'] == size].index
            # Ensure we don't re-label something that's already a title or list item
            df.loc[indices_to_label, 'label'] = level

    return df

def process_unlabelled_csv(input_path: str, output_path: str):
    """
    Reads an unlabelled CSV, applies labeling logic, and saves the result.

    Args:
        input_path (str): The path to the unlabelled input CSV file.
        output_path (str): The path where the labelled output CSV will be saved.
    """
    try:
        # Read the unlabelled CSV
        unlabelled_df = pd.read_csv(input_path)
        print(f"Successfully read {len(unlabelled_df)} rows from {input_path}")

        # Group data by source PDF and apply the labeling function to each group
        # This ensures that styling rules are interpreted on a per-document basis
        labelled_dfs = []
        for pdf_name, group in unlabelled_df.groupby('source_pdf'):
            print(f"Processing: {pdf_name}...")
            # Ensure all expected columns exist, fill with default if not
            if 'font_size_rank' not in group.columns:
                group['font_size_rank'] = group['font_size'].rank(method='dense', ascending=False)
            
            labelled_group = assign_labels(group.copy())
            labelled_dfs.append(labelled_group)

        # Combine the labelled groups back into a single DataFrame
        final_df = pd.concat(labelled_dfs)

        # Reorder columns to have 'label' right after 'source_pdf'
        cols_to_check = ['source_pdf', 'text']
        original_cols = [col for col in unlabelled_df.columns if col not in cols_to_check]
        final_df = final_df[['source_pdf', 'label', 'text'] + original_cols]
        
        # Save the final labelled DataFrame
        final_df.to_csv(output_path, index=False)
        print(f"\nSuccessfully saved labelled data to {output_path}")

    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# if __name__ == '__main__':
#     # --- Instructions for Use ---
#     # 1. Place your unlabelled CSV file in the same directory as this script.
#     # 2. Change 'unlabelled_data.csv' to the name of your file.
#     # 3. Change 'labelled_output.csv' to your desired output file name.
#     # 4. Run the script.

#     # This example assumes your unlabelled CSV is named 'labelled.csv' based on the uploaded file.
#     input_csv_path = 'unlabelled_data.csv' # CHANGED to match uploaded file
#     output_csv_path = 'labelled_output.csv' # CHANGED to new output name
#     process_unlabelled_csv(input_csv_path, output_csv_path)

