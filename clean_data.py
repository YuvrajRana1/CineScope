import pandas as pd

def clean_netflix_data(input_file='netflix_titles.csv', output_file='netflix_cleaned.csv'):
    # Load the dataset
    print("📥 Loading dataset...")
    df = pd.read_csv(input_file)

    print("🔍 Initial data shape:", df.shape)

    # Drop rows with critical missing values
    df.dropna(subset=['title', 'country', 'release_year', 'type', 'listed_in'], inplace=True)

    # Clean country: Keep only the first country if multiple are listed
    df['country'] = df['country'].apply(lambda x: x.split(',')[0].strip())

    # Extract main genre from listed_in
    df['genre'] = df['listed_in'].apply(lambda x: x.split(',')[0].strip())

    # Copy relevant columns into a new DataFrame
    cleaned_df = df[['title', 'type', 'genre', 'release_year', 'rating', 'country']].copy()

    # Rename columns for dashboard readability
    cleaned_df.rename(columns={
        'release_year': 'year',
        'country': 'region'
    }, inplace=True)

    # Display a preview
    print("✅ Cleaned data preview:")
    print(cleaned_df.head())

    # Save to CSV
    cleaned_df.to_csv(output_file, index=False)
    print(f"📁 Cleaned dataset saved as '{output_file}'.")

if __name__ == "__main__":
    clean_netflix_data()
