from serpapi import GoogleSearch

query = "best python libraries 2025"

# Configure the SerpApi client with your API key
params = {
    'q': query,
    'api_key': '', 
    'num': 5  
}

# Perform the search using SerpApi
search = GoogleSearch(params)
results = search.get_dict()

# Print the URLs of the search results
for result in results.get('organic_results', []):
    print(result.get('link'))
# API configuration
