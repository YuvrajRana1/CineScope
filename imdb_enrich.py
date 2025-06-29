import pandas as pd
from imdb import IMDb
import time

# Initialize IMDb client
ia = IMDb()

# Load cleaned Netflix data
df = pd.read_csv("netflix_cleaned.csv")

# Avoid duplicates
titles = df[['title', 'year']].drop_duplicates()
results = []

print("🔍 Fetching data from IMDb...")
for index, row in titles.iterrows():
    title = row['title']
    year = int(row['year'])
    
    try:
        # Search for the title
        search_results = ia.search_movie(title)
        match = None

        # Match with year
        for item in search_results:
            if item.get('year') == year:
                match = item
                break

        if match:
            ia.update(match)
            results.append({
                "title": title,
                "year": year,
                "imdb_rating": match.get('rating'),
                "imdb_votes": match.get('votes'),
                "genres_imdb": ", ".join(match.get('genres', []))
            })
        else:
            results.append({
                "title": title,
                "year": year,
                "imdb_rating": None,
                "imdb_votes": None,
                "genres_imdb": None
            })
    except Exception as e:
        print(f"❌ Error for {title}: {e}")
        results.append({
            "title": title,
            "year": year,
            "imdb_rating": None,
            "imdb_votes": None,
            "genres_imdb": None
        })
    
    time.sleep(0.2)  # polite delay

# Save results
imdb_df = pd.DataFrame(results)
merged = pd.merge(df, imdb_df, on=['title', 'year'], how='left')
merged.to_csv("netflix_imdb_enriched.csv", index=False)

print("✅ IMDb enrichment done. File saved as 'netflix_imdb_enriched.csv'")
