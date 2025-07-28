import fitz
import os
import pandas as pd
from statistics import mean

def is_bullet(text: str) -> bool:
    bullets = ['•', '-', '*', '–', '—']
    stripped = text.lstrip()
    return any(stripped.startswith(b) for b in bullets)

def extract_line_features(pdf_path, line_thresh: float = 2.0):
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    rows = []

    for page_num, page in enumerate(doc, start=1):
        words = page.get_text("words") or []
        if not words:
            continue
        words.sort(key=lambda w: (w[1], w[0]))

        raw_lines = []
        current = [words[0]]
        for w in words[1:]:
            if abs(w[1] - current[-1][1]) <= line_thresh:
                current.append(w)
            else:
                raw_lines.append(current)
                current = [w]
        raw_lines.append(current)

        for line in raw_lines:
            line.sort(key=lambda w: w[0])
            xs = [w[0] for w in line]
            ys = [w[1] for w in line]
            x0, y0 = min(xs), min(ys)
            x1 = max(w[2] for w in line)
            y1 = max(w[3] for w in line)
            text = " ".join(w[4] for w in line).strip()
            if not text:
                continue

            spans = []
            for blk in page.get_text("dict")["blocks"]:
                for ln in blk.get('lines', []):
                    for sp in ln.get('spans', []):
                        sx0, sy0, sx1, sy1 = sp['bbox']
                        if not (sx1 < x0 or sx0 > x1 or sy1 < y0 or sy0 > y1):
                            spans.append(sp)

            char_count = bold_chars = ital_chars = under_chars = 0
            font_sizes, x_positions, y_positions = [], [], []
            for sp in spans:
                span_text = sp.get('text', '').strip()
                if not span_text:
                    continue
                n = len(span_text)
                char_count += n
                font_sizes.append(sp.get('size', 0))
                x_positions.append(sp['bbox'][0])
                y_positions.append(sp['bbox'][1])
                fn = sp.get('font', '').lower()
                if 'bold' in fn:
                    bold_chars += n
                if 'italic' in fn or 'oblique' in fn:
                    ital_chars += n
                if 'underline' in fn:
                    under_chars += n

            avg_font = round(mean(font_sizes), 2) if font_sizes else 0
            indent_x = round(min(x_positions), 2) if x_positions else round(x0, 2)
            line_height = round(y1 - y0, 2)
            line_width = round(x1 - x0, 2)
            center_x = round((x0 + x1) / 2, 2)
            center_y = round((y0 + y1) / 2, 2)

            rows.append({
                'source_pdf': os.path.basename(pdf_path),
                'label': None,
                'text': text,
                'page': page_num,
                'font_size': avg_font,
                'font_size_rank': None,
                'bold_ratio': round(bold_chars / char_count, 2) if char_count else 0,
                'italic_ratio': round(ital_chars / char_count, 2) if char_count else 0,
                'underline_ratio': round(under_chars / char_count, 2) if char_count else 0,
                'indent_x': indent_x,
                'x0': round(x0, 2),
                'y0': round(y0, 2),
                'x1': round(x1, 2),
                'y1': round(y1, 2),
                'line_height': line_height,
                'line_width': line_width,
                'center_x': center_x,
                'center_y': center_y,
                'position_top': center_y < page.rect.height * 0.25,
                'position_bottom': center_y > page.rect.height * 0.75,
                'ends_with_period': text.endswith('.'),
                'ends_with_colon': text.endswith(':'),
                'ends_with_hyphen': text.endswith('-'),
                'has_quotes': any(q in text for q in ['"', '\'', '“', '”']),
                'bullet_char': is_bullet(text),
                'text_length': len(text),
                'num_words': len(text.split()),
                'all_uppercase': text.isupper(),
                'capitalized_words_ratio': round(
                    sum(1 for w in text.split() if w[:1].isupper()) / len(text.split()), 2
                ) if text.split() else 0,
                'page_number': page_num,
                'relative_page_pos': round(page_num / total_pages, 2),
                'is_first_page': page_num == 1,
                'is_last_page': page_num == total_pages
            })

    df = pd.DataFrame(rows)
    if not df.empty:
        df['font_size_rank'] = df.groupby('source_pdf')['font_size'].rank(method='dense', ascending=False).astype(int)
    return df

def process_folder(input_dir, output_csv):
    all_data = []
    for file in os.listdir(input_dir):
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_dir, file)
            df = extract_line_features(pdf_path)
            all_data.append(df)
            print(f"✔ Processed: {file} → {len(df)} lines")

    # Concatenate all dataframes and write to one CSV
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_csv(output_csv, index=False)
    print(f"\n✅ Saved {len(final_df)} total lines to {output_csv}")

# if __name__ == "__main__":
#     # input_dir = "input"
#     # output_csv = "unlabelled_data.csv"
#     # process_folder(input_dir, output_csv)
