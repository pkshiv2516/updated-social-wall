from flask import Flask, render_template
import os
import pandas as pd
import random
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
csv_file = "social_posts.csv"

def fetch_og_data(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        def get_tag(property_name):
            tag = soup.find('meta', property=property_name)
            return tag['content'] if tag else ''

        return {
            'url': url,
            'title': get_tag('og:title'),
            'description': get_tag('og:description'),
            'image': get_tag('og:image'),
            'site_name': get_tag('og:site_name'),
        }

    except Exception as e:
        print(f"Error fetching OG data for {url}: {e}")
        return {
            'url': url,
            'title': 'Link Preview',
            'description': 'No preview available',
            'image': '',
            'site_name': ''
        }

def load_posts():
    """Load posts from CSV and group by platform."""
    if not os.path.exists(csv_file):
        return {"Instagram": [], "Twitter": [], "LinkedIn": []}
    
    posts = pd.read_csv(csv_file)
    if posts.empty:
        return {"Instagram": [], "Twitter": [], "LinkedIn": []}
    
    # Group posts by platform
    grouped_posts = {
        "Instagram": [],
        "Twitter": [],
        "LinkedIn": []
    }
    
    for _, row in posts.iterrows():
        platform = row['platform']
        if platform in grouped_posts:
            post_data = {
                "url": row['url'],
                "extraction_date": row['extraction_date']
            }
            if platform == "LinkedIn":
                post_data["content"] = row.get('content', '')
            grouped_posts[platform].append(post_data)
    
    return grouped_posts

posts_by_platform = load_posts()
all_posts = []
for platform, posts in posts_by_platform.items():
    for post in posts:
        post['platform'] = platform
        all_posts.append(post)

@app.route('/')
def index():
    """Render the unified social wall page with randomly shuffled posts from all platforms."""
       
    # Combine all posts and shuffle randomly    
    random.shuffle(all_posts)
    print(all_posts)
    
    return render_template('social_wall.html', posts=all_posts)
# @app.route('/')
# def index():

#     preview_posts = [fetch_og_data(post['url']) for post in all_posts]

#     return render_template("test.html", posts=preview_posts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)