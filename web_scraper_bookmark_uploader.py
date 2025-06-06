import csv
import time
import random
import requests
from urllib.parse import urlparse
from serpapi import GoogleSearch
import os

# --- Configuration ---
BASE_API_URL = "https://xi9d.pythonanywhere.com/api"
BOOKMARKS_ENDPOINT = f"{BASE_API_URL}/bookmarks"
CATEGORIES_ENDPOINT = f"{BASE_API_URL}/categories"
API_KEY = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB2Y3N1b2FidWx0bWF4YXdiYXJ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc0NTMwOTUsImV4cCI6MjA2MzAyOTA5NX0.NY-E0bM1hYwRelGWvVSbTrc9MxET_Fd04gS7zAshoN0"
SERPAPI_KEY = "97e1fba8d97e26b00c792dc6061aede436e3fca822dbc4a0e6085c2622e32dd9"
CSV_FILE = 'scraped_bookmarks.csv'
RESULTS_PER_QUERY = 10
TARGET_QUERIES = 1000  # Target number of queries

# Expanded search queries for different topics
BASE_SEARCH_QUERIES = [
    # Technology & Programming
    'best programming tools 2025', 'coding bootcamps online', 'web development frameworks',
    'mobile app development platforms', 'database management tools', 'cloud computing services',
    'cybersecurity resources', 'artificial intelligence platforms', 'machine learning courses',
    'data science tools', 'API documentation sites', 'developer communities',
    
    # Productivity & Business
    'project management software', 'time tracking apps', 'note taking applications',
    'team collaboration tools', 'business planning resources', 'marketing automation',
    'email marketing platforms', 'CRM software solutions', 'accounting software',
    'invoice generation tools', 'freelancing platforms', 'remote work tools',
    
    # Education & Learning
    'online learning platforms', 'skill development courses', 'certification programs',
    'language learning apps', 'math learning resources', 'science education sites',
    'history learning platforms', 'art education online', 'music learning apps',
    'cooking classes online', 'photography tutorials', 'writing improvement tools',
    
    # Health & Fitness
    'fitness tracking apps', 'workout planning tools', 'nutrition tracking',
    'meditation apps', 'mental health resources', 'yoga instruction videos',
    'running apps', 'weight loss programs', 'healthy recipe sites',
    'sleep tracking apps', 'healthcare platforms', 'telemedicine services',
    
    # Finance & Investment
    'budgeting apps', 'investment platforms', 'cryptocurrency exchanges',
    'personal finance tools', 'tax preparation software', 'banking apps',
    'credit monitoring services', 'loan comparison sites', 'insurance platforms',
    'retirement planning tools', 'trading platforms', 'financial news sites',
    
    # Entertainment & Media
    'streaming services', 'podcast platforms', 'music discovery apps',
    'video editing software', 'photo editing tools', 'gaming platforms',
    'book reading apps', 'comic reading platforms', 'movie review sites',
    'TV show tracking', 'sports news sites', 'entertainment news',
    
    # Travel & Lifestyle
    'travel booking sites', 'hotel comparison', 'flight booking platforms',
    'travel planning apps', 'restaurant discovery', 'food delivery services',
    'recipe sharing sites', 'home improvement tools', 'gardening resources',
    'pet care apps', 'weather apps', 'local event platforms',
    
    # Shopping & E-commerce
    'online shopping platforms', 'price comparison tools', 'coupon sites',
    'marketplace platforms', 'auction sites', 'fashion retailers',
    'electronics stores', 'book stores online', 'grocery delivery',
    'specialty stores', 'handmade crafts platforms', 'wholesale suppliers',
    
    # News & Information
    'news aggregators', 'fact checking sites', 'research databases',
    'academic journals', 'government resources', 'legal information',
    'medical information sites', 'weather forecasting', 'traffic updates',
    'local news sources', 'international news', 'technology news',
    
    # Social & Community
    'social networking sites', 'community forums', 'discussion platforms',
    'messaging apps', 'video calling platforms', 'dating apps',
    'hobby communities', 'professional networks', 'local community groups',
    'volunteer platforms', 'event planning tools', 'meetup platforms'
]

# Modifiers to create variations
QUERY_MODIFIERS = [
    'best', 'top', 'popular', 'recommended', 'free', 'premium', 'professional',
    '2025', '2024', 'latest', 'new', 'trending', 'ultimate', 'complete',
    'beginner', 'advanced', 'expert', 'simple', 'easy', 'comprehensive'
]

QUERY_SUFFIXES = [
    'tools', 'apps', 'websites', 'platforms', 'services', 'resources',
    'software', 'solutions', 'programs', 'systems', 'applications'
]

# --- Global Variables ---
categories_cache = {}
subcategories_cache = {}

# --- Functions ---
def load_existing_urls_from_csv():
    """Load existing URLs from CSV file to avoid duplicates."""
    existing_urls = set()
    
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'url' in row and row['url']:
                        existing_urls.add(row['url'])
            print(f"📝 Loaded {len(existing_urls)} existing URLs from {CSV_FILE}")
        except Exception as e:
            print(f"⚠️ Error reading existing CSV: {e}")
    else:
        print(f"📝 No existing CSV file found, starting fresh")
    
    return existing_urls

def generate_search_queries():
    """Generate a large number of search query variations."""
    queries = []
    
    # Add base queries
    queries.extend(BASE_SEARCH_QUERIES)
    
    # Generate variations with modifiers
    for base_query in BASE_SEARCH_QUERIES[:50]:  # Use first 50 base queries for variations
        words = base_query.split()
        
        # Add modifier at the beginning
        for modifier in QUERY_MODIFIERS[:8]:  # Use first 8 modifiers
            new_query = f"{modifier} {base_query}"
            queries.append(new_query)
        
        # Replace last word with different suffix
        if len(words) > 1:
            for suffix in QUERY_SUFFIXES[:6]:  # Use first 6 suffixes
                new_query = ' '.join(words[:-1]) + f" {suffix}"
                queries.append(new_query)
    
    # Add some specific trending topics
    trending_queries = [
        'AI chatbot platforms', 'blockchain development tools', 'NFT marketplaces',
        'sustainable living apps', 'electric vehicle resources', 'remote learning platforms',
        'virtual reality applications', 'augmented reality tools', 'IoT development platforms',
        'quantum computing resources', 'green energy calculators', 'carbon footprint trackers',
        'minimalist lifestyle apps', 'digital nomad resources', 'gig economy platforms',
        'mental wellness apps', 'mindfulness meditation', 'productivity hacks tools',
        'side hustle platforms', 'passive income resources', 'dropshipping tools',
        'print on demand services', 'affiliate marketing platforms', 'content creation tools',
        'video streaming tools', 'podcast hosting platforms', 'newsletter platforms',
        'community building tools', 'customer feedback platforms', 'survey tools',
        'analytics dashboards', 'heat mapping tools', 'conversion optimization',
        'SEO analysis tools', 'keyword research platforms', 'backlink analysis tools'
    ]
    
    queries.extend(trending_queries)
    
    # Remove duplicates and shuffle
    queries = list(set(queries))
    random.shuffle(queries)
    
    print(f"🎯 Generated {len(queries)} unique search queries")
    return queries

def fetch_categories_and_subcategories():
    """Fetch all categories and subcategories from the API and cache them."""
    global categories_cache, subcategories_cache
    
    try:
        print("📋 Fetching categories and subcategories...")
        response = requests.get(
            CATEGORIES_ENDPOINT,
            headers={'Authorization': API_KEY, 'Content-Type': 'application/json'}
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to fetch categories: {response.status_code} - {response.text}")
            return False
            
        categories_data = response.json()
        
        for category in categories_data:
            category_name = category['name']
            categories_cache[category_name] = category['id']
            
            for subcategory in category.get('subcategories', []):
                subcategory_name = subcategory['name']
                subcategories_cache[subcategory_name] = {
                    'id': subcategory['id'],
                    'category_name': category_name
                }
        
        print(f"✅ Loaded {len(categories_cache)} categories and {len(subcategories_cache)} subcategories")
        return True
        
    except Exception as e:
        print(f"❌ Error fetching categories: {e}")
        return False

def find_best_subcategory(query, url_domain):
    """Find the best matching subcategory for a query and URL."""
    query_lower = query.lower()
    domain_lower = url_domain.lower()
    
    # Enhanced keyword mappings for better categorization
    keyword_mappings = {
        'forum': '🌐 Forums & Online Communities',
        'community': '🌐 Forums & Online Communities',
        'reddit': '🌐 Forums & Online Communities',
        'discord': '🌐 Forums & Online Communities',
        'programming': '🛠️ Coding & Development Tools',
        'coding': '🛠️ Coding & Development Tools',
        'development': '🛠️ Coding & Development Tools',
        'github': '🛠️ Coding & Development Tools',
        'developer': '🛠️ Coding & Development Tools',
        'api': '📖 API & Developer Documentation',
        'documentation': '📖 API & Developer Documentation',
        'cryptocurrency': '💹 Cryptocurrency & Blockchain',
        'crypto': '💹 Cryptocurrency & Blockchain',
        'bitcoin': '💹 Cryptocurrency & Blockchain',
        'blockchain': '💹 Cryptocurrency & Blockchain',
        'learning': '📚 Free Educational Resources',
        'course': '📚 Online Courses & Certifications',
        'education': '📚 Free Educational Resources',
        'tutorial': '🧩 Skill-Building Tutorials',
        'certification': '📚 Online Courses & Certifications',
        'fitness': '💪 Fitness & Workout Plans',
        'workout': '💪 Fitness & Workout Plans',
        'health': '💪 Fitness & Workout Plans',
        'recipe': '🍽️ Recipes & Meal Planning',
        'cooking': '🍽️ Recipes & Meal Planning',
        'food': '🍽️ Recipes & Meal Planning',
        'travel': '🗺️ Destination Guides & Inspiration',
        'booking': '🏨 Accommodation Booking',
        'hotel': '🏨 Accommodation Booking',
        'flight': '🛫 Flights & Transportation',
        'design': '🎭 Digital Art & Graphic Design',
        'graphics': '🎭 Digital Art & Graphic Design',
        'art': '🎭 Digital Art & Graphic Design',
        'music': '🎵 Music Streaming & Discovery',
        'streaming': '📺 Video Streaming & Movies',
        'video': '📺 Video Streaming & Movies',
        'podcast': '🎵 Music Streaming & Discovery',
        'news': '🗞️ Global News & Current Events',
        'job': '🎯 Job Search & Applications',
        'career': '🎯 Job Search & Applications',
        'freelance': '🎯 Job Search & Applications',
        'shopping': '🛒 E-Commerce & Online Shopping',
        'ecommerce': '🛒 E-Commerce & Online Shopping',
        'store': '🛒 E-Commerce & Online Shopping',
        'social': '📱 Social Media & Content Sharing',
        'network': '🤝 Networking & Professional Profiles',
        'productivity': '⚡ Productivity & Task Management',
        'project': '⚡ Productivity & Task Management',
        'finance': '💰 Personal Finance & Investment',
        'investment': '💰 Personal Finance & Investment',
        'budget': '💰 Personal Finance & Investment',
        'marketing': '📈 Digital Marketing & SEO Tools',
        'seo': '📈 Digital Marketing & SEO Tools',
        'analytics': '📊 Analytics & Data Visualization'
    }
    
    # Check for keyword matches
    combined_text = f"{query_lower} {domain_lower}"
    for keyword, subcategory in keyword_mappings.items():
        if keyword in combined_text and subcategory in subcategories_cache:
            return subcategories_cache[subcategory]['id']
    
    # Default fallback - try to find a general subcategory
    fallback_subcategories = [
        '🌐 Search Engines & Directories',
        '🔎 Niche Content Aggregators',
        '🗂️ Bookmark & Content Curation'
    ]
    
    for fallback in fallback_subcategories:
        if fallback in subcategories_cache:
            return subcategories_cache[fallback]['id']
    
    # If nothing found, return the first available subcategory
    if subcategories_cache:
        return list(subcategories_cache.values())[0]['id']
    
    return None

def search_serpapi(query):
    """Perform a search using SerpApi and return result links."""
    print(f"🔍 Searching: {query}")
    params = {
        'q': query,
        'api_key': SERPAPI_KEY,
        'num': RESULTS_PER_QUERY,
        'gl': 'us',  # Country
        'hl': 'en'   # Language
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if 'organic_results' not in results:
            print(f"⚠️ No organic results found for: {query}")
            return []
            
        links = []
        for result in results['organic_results']:
            if 'link' in result:
                links.append({
                    'url': result['link'],
                    'title': result.get('title', ''),
                    'snippet': result.get('snippet', '')
                })
        
        print(f"✅ Found {len(links)} results for: {query}")
        return links
        
    except Exception as e:
        print(f"❌ Search error for '{query}': {e}")
        return []

def clean_title(title, domain):
    """Clean and improve the bookmark title."""
    if not title or title.lower() == domain.lower():
        # Create a better title from domain
        return domain.replace('.com', '').replace('.org', '').replace('.net', '').title()
    
    # Remove common suffixes and clean up
    title = title.replace(' - Wikipedia', '')
    title = title.replace(' | Official Site', '')
    title = title.replace(' - Official Website', '')
    
    # Limit length
    if len(title) > 100:
        title = title[:97] + "..."
    
    return title

def append_to_csv(bookmark):
    """Append a single bookmark to CSV file."""
    try:
        file_exists = os.path.exists(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['title', 'url', 'subcategory_id', 'description', 'tags'])
            
            if not file_exists:
                writer.writeheader()
                
            writer.writerow({
                'title': bookmark['title'],
                'url': bookmark['url'],
                'subcategory_id': bookmark['subcategory_id'],
                'description': bookmark['description'],
                'tags': ','.join(bookmark.get('tags', []))
            })
            
    except Exception as e:
        print(f"❌ Error appending to CSV: {e}")

def upload_bookmark(bookmark):
    """Upload a single bookmark to the API."""
    try:
        # Prepare the payload according to API requirements
        payload = {
            'subcategory_id': bookmark['subcategory_id'],
            'title': bookmark['title'],
            'url': bookmark['url'],
            'description': bookmark.get('description', ''),
            'tags': bookmark.get('tags', []),
            'is_favorite': False
        }
        
        response = requests.post(
            BOOKMARKS_ENDPOINT,
            json=payload,
            headers={'Authorization': API_KEY, 'Content-Type': 'application/json'}
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Uploaded: {bookmark['title']}")
            return True
        else:
            print(f"❌ Failed to upload {bookmark['title']} ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload error for {bookmark['title']}: {e}")
        return False

def extract_domain(url):
    """Extract clean domain name from URL."""
    try:
        domain = urlparse(url).netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return url

def run():
    """Main function to run the bookmark scraper and uploader."""
    print("🚀 Starting Enhanced Bookmark Scraper & Uploader...")
    print(f"🎯 Target: {TARGET_QUERIES} queries")
    
    # Load existing URLs to avoid duplicates
    existing_urls = load_existing_urls_from_csv()
    
    # First, fetch categories and subcategories
    if not fetch_categories_and_subcategories():
        print("❌ Cannot proceed without categories data")
        return
    
    # Generate search queries
    search_queries = generate_search_queries()
    
    # Limit to target number of queries
    if len(search_queries) > TARGET_QUERIES:
        search_queries = search_queries[:TARGET_QUERIES]
    
    successful_uploads = 0
    failed_uploads = 0
    new_urls_found = 0
    duplicate_urls_skipped = 0
    
    print(f"\n🔍 Starting search with {len(search_queries)} queries...")
    
    for i, query in enumerate(search_queries, 1):
        print(f"\n--- Query {i}/{len(search_queries)} ---")
        
        # Get search results
        search_results = search_serpapi(query)
        
        if not search_results:
            print(f"⚠️ No results for query: {query}")
            continue
        
        for result in search_results:
            url = result['url']
            
            # Skip if URL already exists
            if url in existing_urls:
                duplicate_urls_skipped += 1
                continue
                
            # Add to existing URLs set
            existing_urls.add(url)
            new_urls_found += 1
            
            domain = extract_domain(url)
            
            # Find best subcategory
            subcategory_id = find_best_subcategory(query, domain)
            
            if not subcategory_id:
                print(f"⚠️ No suitable subcategory found for: {domain}")
                continue
            
            # Clean and prepare bookmark data
            title = clean_title(result['title'], domain)
            description = result.get('snippet', f'Resource found for: {query}')[:500]  # Limit description length
            
            bookmark = {
                'title': title,
                'url': url,
                'subcategory_id': subcategory_id,
                'description': description,
                'tags': query.split()[:5]  # Limit to 5 tags
            }
            
            # Upload bookmark and save to CSV
            if upload_bookmark(bookmark):
                successful_uploads += 1
                append_to_csv(bookmark)
            else:
                failed_uploads += 1
            
            # Rate limiting
            time.sleep(random.uniform(0.5, 1.5))
        
        # Progress update every 50 queries
        if i % 50 == 0:
            print(f"\n📊 Progress Update ({i}/{len(search_queries)}):")
            print(f"   • New URLs found: {new_urls_found}")
            print(f"   • Duplicates skipped: {duplicate_urls_skipped}")
            print(f"   • Successful uploads: {successful_uploads}")
            print(f"   • Failed uploads: {failed_uploads}")
        
        # Longer pause between queries to avoid rate limiting
        if i < len(search_queries):
            time.sleep(random.uniform(2, 4))
    
    # Final summary
    print(f"\n🎉 Process completed!")
    print(f"📊 Final Summary:")
    print(f"   • Total queries processed: {len(search_queries)}")
    print(f"   • New URLs found: {new_urls_found}")
    print(f"   • Duplicate URLs skipped: {duplicate_urls_skipped}")
    print(f"   • Successful uploads: {successful_uploads}")
    print(f"   • Failed uploads: {failed_uploads}")
    print(f"   • CSV file updated: {CSV_FILE}")

# --- Entry Point ---
if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user.")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()