from serpapi import GoogleSearch

query = "best python libraries 2025"

# Configure the SerpApi client with your API key
params = {
    'q': query,
    'api_key': '97e1fba8d97e26b00c792dc6061aede436e3fca822dbc4a0e6085c2622e32dd9', 
    'num': 5  
}

# Perform the search using SerpApi
search = GoogleSearch(params)
results = search.get_dict()

# Print the URLs of the search results
for result in results.get('organic_results', []):
    print(result.get('link'))
# API configuration
API_BASE_URL = 'https://xi9d.pythonanywhere.com/api'
API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2Y3N1b2FidWx0bWF4YXdiYXJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0NTMwOTUsImV4cCI6MjA2MzAyOTA5NX0.NY-E0bM1hYwRelGWvVSbTrc9MxET_Fd04gS7zAshoN0'  # Replace with your actual API key after signing in
CSV_FILE = 'travel_bookmarks.csv'