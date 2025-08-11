import os
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

class InstagramHandler:
    def __init__(self):
        self.username = "airc.woxsen"
        self.password = "Woxsen@1234"
        self.csv_file = "social_posts.csv"
        self.driver = None

    def login(self):
        """Log into Instagram using Selenium."""
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.instagram.com/accounts/login/")
        time.sleep(5)

        self.driver.find_element(By.NAME, "username").send_keys(self.username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)

        try:
            not_now_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            not_now_button.click()
        except:
            pass

    def fetch_posts(self):
        """Fetch posts from a profile using BeautifulSoup."""
        self.driver.get("https://www.instagram.com/woxsen_university/")
        time.sleep(5)

        for _ in range(20):
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(3)

        html = self.driver.page_source
        self.driver.quit()

        soup = BeautifulSoup(html, "html.parser")
        post_data = []

        for post in soup.find_all("a", href=True):
            link = post["href"]
            if "/p/" in link:
                post_id = link.split("/")[-2]
                post_url = f"https://www.instagram.com/p/{post_id}/embed/"
                print(post_url)
                post_data.append({
                    'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                    'platform': 'Instagram',
                    'url': post_url
                })

        self.save_to_csv(post_data)
        print(f"Successfully fetched {len(post_data)} posts")

    def save_to_csv(self, post_data):
        df = pd.DataFrame(post_data)

        if os.path.exists(self.csv_file) and os.path.getsize(self.csv_file) > 0:
            existing_df = pd.read_csv(self.csv_file)
            df = df[~df['url'].isin(existing_df['url'])]
            df.to_csv(self.csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.csv_file, index=False)

        print(f"Saved {len(df)} new posts to {self.csv_file}")

# Run the script
bot = InstagramHandler()
bot.login()
bot.fetch_posts()