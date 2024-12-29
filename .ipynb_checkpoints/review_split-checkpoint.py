import pandas as pd
import re

# Function to split strings on commas
def split_on_commas(value):
    return value.split(',') if pd.notna(value) else []


# Function to check if splits match in length
def validate_split_lengths(*splits):
    lengths = [len(split) for split in splits]
    return all(length == lengths[0] for length in lengths)


# Function to split on commas followed by capital letters
def split_on_commas_followed_by_caps(value):
    return re.split(r',(?=[A-Z])', value) if pd.notna(value) else []


def split_on_unspaced_commas(value):
    # return re.split(r'(?<=[!.?]),', value) if pd.notna(value) else []
    return re.split(r',(?=\S)', value) if pd.notna(value) else []




def process_row(row):
    user_ids = split_on_commas(row['user_id'])
    review_ids = split_on_commas(row['review_id'])
    review_titles = split_on_commas(row['review_title'])
    review_contents = split_on_commas(row['review_content'])

    if validate_split_lengths(user_ids, review_ids, review_titles, review_contents):
        return 'good_to_go', len(user_ids)

    review_titles_alt = split_on_commas_followed_by_caps(row['review_title'])
    review_contents_alt = split_on_commas_followed_by_caps(row['review_content'])

    if validate_split_lengths(user_ids, review_ids, review_titles_alt, review_contents_alt):
        return 'fixed_with_caps', len(user_ids)

    review_titles_punctuated = split_on_unspaced_commas(row['review_title'])
    review_contents_punctuated = split_on_unspaced_commas(row['review_content'])

    if validate_split_lengths(user_ids, review_ids, review_titles_punctuated, review_contents_punctuated):
        return 'fixed_with_unspaced_commas', len(user_ids)

    return 'unsalvageable', None




def process_dataframe(df):
    results = {'good_to_go': 0, 'fixed_with_caps': 0, 'fixed_with_unspaced_commas': 0, 'unsalvageable': 0, 'percent_salvaged': 0}
    good_rows = []

    for _, row in df.iterrows():
        status, count = process_row(row)
        results[status] += 1

        if status != 'unsalvageable':
            user_ids = split_on_commas(row['user_id'])
            review_ids = split_on_commas(row['review_id'])
            if status == 'good_to_go':
                review_titles = split_on_commas(row['review_title'])
                review_contents = split_on_commas(row['review_content'])
            elif status == 'fixed_with_caps':
                review_titles = split_on_commas_followed_by_caps(row['review_title'])
                review_contents = split_on_commas_followed_by_caps(row['review_content'])
            else:  # fixed_with_punctuated
                review_titles = split_on_unspaced_commas(row['review_title'])
                review_contents = split_on_unspaced_commas(row['review_content'])

            for user_id, review_id, review_title, review_content in zip(user_ids, review_ids, review_titles, review_contents):
                good_rows.append({
                    'user_id': user_id,
                    'review_id': review_id,
                    'review_title': review_title,
                    'review_content': review_content
                })
    results['percent_salvaged'] = round(
        ((df.shape[0] - results['unsalvageable']) / df.shape[0]) * 100, 2
    )
    return pd.DataFrame(good_rows), results