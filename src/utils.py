def get_director(crew_list):
    """Extract director name from crew list."""
    for person in crew_list:
        if person['job'] == 'Director':
            return person['name']
    return None

def get_list(feature_list):
    """Extract top 3 names from a feature list."""
    if isinstance(feature_list, list):
        names = [item['name'] for item in feature_list]
        if len(names) > 3:
            names = names[:3]
        return names
    return []

def clean_data(data):
    """Clean and normalize text data."""
    if isinstance(data, list):
        return [str.lower(item.replace(' ', '')) for item in data]
    elif isinstance(data, str):
        return str.lower(data.replace(' ', ''))
    else:
        return ''

def create_soup(row):
    """Combine all features into a single text string."""
    keywords = ' '.join(row['keywords']) if isinstance(row['keywords'], list) else ''
    cast = ' '.join(row['cast']) if isinstance(row['cast'], list) else ''
    genres = ' '.join(row['genres']) if isinstance(row['genres'], list) else ''
    director = row['director'] if isinstance(row['director'], str) else ''
    
    return f"{keywords} {cast} {director} {genres}"