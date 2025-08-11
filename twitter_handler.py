import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class TwitterHandler:
    def __init__(self):
        self.email = "shrivathsavkotla.2007@gmail.com"
        self.username = "KShrivathsav"
        self.password = "shri07#Chinnu"
        self.csv_file = "social_posts.csv"
        self.driver = None

    def login(self):
        """Log into Twitter using Selenium."""
        self.driver = webdriver.Chrome()
        self.driver.get("https://twitter.com/login")
        time.sleep(5)

        self.driver.find_element(By.NAME, "text").send_keys(self.email)
        self.driver.find_element(By.NAME, "text").send_keys(Keys.RETURN)
        time.sleep(3)

        try:
            username_field = self.driver.find_element(By.NAME, "text")
            username_field.send_keys(self.username)
            username_field.send_keys(Keys.RETURN)
            time.sleep(3)
        except:
            pass

        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)
        time.sleep(5)

    def fetch_posts(self):
        """Fetch tweets with #woxsenuniversity hashtag using Selenium and BeautifulSoup."""
        self.driver.get("https://twitter.com/search?q=%23woxsen&f=live")
        time.sleep(5)

        for _ in range(5):
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(3)

        html = self.driver.page_source
        self.driver.quit()

        soup = BeautifulSoup(html, "html.parser")
        post_data = []

        for tweet in soup.find_all("article"):
            tweet_text = tweet.get_text(separator=" ", strip=True)

            tweet_link = None
            for link in tweet.find_all("a", href=True):
                if "/status/" in link["href"]:
                    tweet_id = link["href"].split("/")[-1]
                    tweet_link = f"https://platform.twitter.com/embed/Tweet.html?id={tweet_id}"
                    break

            if tweet_link:
                print(tweet_link)
                post_data.append({
                    'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                    'platform': 'Twitter',
                    'url': tweet_link
                })

        self.save_to_csv(post_data)
        print(f"Successfully fetched {len(post_data)} tweets")

    def save_to_csv(self, post_data):
        df = pd.DataFrame(post_data)

        if os.path.exists(self.csv_file) and os.path.getsize(self.csv_file) > 0:
            existing_df = pd.read_csv(self.csv_file)
            df = df[~df['url'].isin(existing_df['url'])]
            df.to_csv(self.csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.csv_file, index=False)

        print(f"Saved {len(df)} new tweets to {self.csv_file}")

# Run the script
bot = TwitterHandler()
bot.login()
bot.fetch_posts()