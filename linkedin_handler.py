import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from bs4 import BeautifulSoup
from PIL import Image

class LinkedInScreenshotHandler:
    def __init__(self):
        self.email = "woxsenailab@gmail.com"
        self.password = "Ai@l@bfaculty@2024"
        self.csv_file = "social_posts.csv"
        self.screenshot_dir = "post_screenshots"
        
        # Create screenshot directory if it doesn't exist
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def take_post_screenshot(self, driver, urn, post_id):
        """Take a screenshot of an individual post using the collapsed embed URL and auto-detect frame."""
        try:
            # Construct the collapsed embed URL as requested
            post_url = f"https://www.linkedin.com/feed/update/urn:li:share:{urn}"
            print(f"Opening post URL: {post_url}")
            
            # Open the post in a new tab
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[-1])
            
            # Navigate to the post
            driver.get(post_url)
            time.sleep(8)  # Wait longer for embed to load
            
            # Wait for the page to load completely
            wait = WebDriverWait(driver, 20)
            
            # Multiple selectors to identify the post frame automatically
            post_frame_selectors = [
                # Main post container selectors
                "div.feed-shared-update-v2",
                "article[data-urn]",
                "div.feed-shared-update-v2__content",
                "div.feed-shared-text",
                "div.scaffold-layout__detail",
                "main.scaffold-layout__main",
                
                # Embed specific selectors
                "div.embed-post",
                "div.share-update-card",
                "div.feed-shared-mini-update-v2",
                
                # Fallback selectors
                "div[data-urn]",
                ".artdeco-card",
                ".update-components-article",
                
                # Generic content selectors
                "main",
                ".main-content",
                "article"
            ]
            
            post_element = None
            found_selector = None
            
            # Try each selector until we find the post frame
            for selector in post_frame_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Check if element has reasonable dimensions
                        size = element.size
                        if size['height'] > 50 and size['width'] > 100:
                            post_element = element
                            found_selector = selector
                            print(f"Found post frame using selector: {selector}")
                            break
                    if post_element:
                        break
                except Exception as e:
                    continue
            
            if post_element:
                # Scroll the post into view and wait
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", post_element)
                time.sleep(3)
                
                # Get element dimensions
                location = post_element.location
                size = post_element.size
                
                print(f"Post frame found - Selector: {found_selector}")
                print(f"Dimensions: {size['width']}x{size['height']} at ({location['x']}, {location['y']})")
                
                # Ensure the element is visible and has reasonable size
                if size['height'] < 100:
                    # Try to expand or find parent container
                    try:
                        parent = post_element.find_element(By.XPATH, "..")
                        if parent.size['height'] > size['height']:
                            post_element = parent
                            location = post_element.location
                            size = post_element.size
                            print(f"Using parent element - New dimensions: {size['width']}x{size['height']}")
                    except:
                        pass
                
                # Take screenshot of the entire viewport first
                temp_screenshot_path = os.path.join(self.screenshot_dir, f"temp_full_{post_id}.png")
                driver.save_screenshot(temp_screenshot_path)
                
                # Open and crop the image
                img = Image.open(temp_screenshot_path)
                
                # Calculate crop coordinates with padding
                padding = 20
                left = max(0, location['x'] - padding)
                top = max(0, location['y'] - padding)
                right = min(img.width, location['x'] + size['width'] + padding)
                bottom = min(img.height, location['y'] + size['height'] + padding)
                
                # Ensure minimum dimensions for readability
                min_width, min_height = 400, 300
                if (right - left) < min_width:
                    center_x = (left + right) / 2
                    left = max(0, center_x - min_width/2)
                    right = min(img.width, left + min_width)
                
                if (bottom - top) < min_height:
                    center_y = (top + bottom) / 2
                    top = max(0, center_y - min_height/2)
                    bottom = min(img.height, top + min_height)
                
                print(f"Cropping coordinates: ({left}, {top}, {right}, {bottom})")
                
                # Crop and save the final image
                cropped_img = img.crop((int(left), int(top), int(right), int(bottom)))
                final_screenshot_path = os.path.join(self.screenshot_dir, f"post_{post_id}.png")
                cropped_img.save(final_screenshot_path, quality=95)
                
                # Clean up temp file
                os.remove(temp_screenshot_path)
                
                print(f"✓ Screenshot saved: {final_screenshot_path}")
                
            else:
                print(f"⚠ No post frame found, taking full page screenshot for {post_id}")
                # Fallback: take full page screenshot
                final_screenshot_path = os.path.join(self.screenshot_dir, f"post_{post_id}_fullpage.png")
                driver.save_screenshot(final_screenshot_path)
            
            # Close current tab and return to main window
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
            return final_screenshot_path
            
        except Exception as e:
            print(f"✗ Error taking screenshot for post {post_id}: {e}")
            # Ensure we return to main window
            try:
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
            except:
                pass
            return None

    def fetch_posts_with_screenshots(self):
        """Fetch posts and take screenshots by opening each post individually."""
        if not self.email or not self.password:
            print("LinkedIn credentials not provided")
            return []

        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        driver = webdriver.Chrome(options=options)
        
        try:
            print("Logging into LinkedIn")
            driver.get("https://linkedin.com/uas/login")
            
            wait = WebDriverWait(driver, 10)
            username = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username.send_keys(self.email)
            
            pword = driver.find_element(By.ID, "password")
            pword.send_keys(self.password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            time.sleep(10)

            print("Searching for #woxsen posts")
            driver.get("https://www.linkedin.com/search/results/content/?keywords=%23woxsen")
            time.sleep(5)

            # First, collect all URNs by scrolling through the search results
            print("Collecting all post URNs...")
            collected_urns = set()
            
            for scroll in range(15):  # Scroll to collect URNs
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                
                posts = soup.find_all("div", class_="feed-shared-update-v2")
                for post in posts:
                    urn = post.get("data-urn")
                    if urn and urn not in collected_urns:
                        collected_urns.add(urn)
                        print(f"Found URN: {urn}")
                
                # Scroll down for more posts
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
                time.sleep(3)
                print(f"Completed scroll {scroll + 1}/15, collected {len(collected_urns)} URNs")

            print(f"Total URNs collected: {len(collected_urns)}")
            
            # Now take screenshots of each post individually
            post_data = []
            for i, urn in enumerate(collected_urns):
                try:
                    # Clean the URN to get the proper format
                    if ":" in urn:
                        urn_parts = urn.split(":")
                        clean_urn = urn_parts[-1] if len(urn_parts) > 1 else urn
                    else:
                        clean_urn = urn
                    
                    post_id = f"{i+1}_{clean_urn}"
                    
                    print(f"Taking screenshot {i+1}/{len(collected_urns)} for URN: {urn}")
                    screenshot_path = self.take_post_screenshot(driver, clean_urn, post_id)
                    
                    if screenshot_path:
                        post_link = f"https://www.linkedin.com/embed/feed/update/{clean_urn}?collapsed=1"
                        direct_link = f"https://www.linkedin.com/feed/update/{clean_urn}?collapsed=1"
                        
                        post_data.append({
                            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'platform': 'LinkedIn',
                            'urn': urn,
                            'clean_urn': clean_urn,
                            'url': post_link,
                            'direct_url': direct_link,
                            'screenshot_path': screenshot_path,
                            'post_id': post_id
                        })
                        print(f"✓ Successfully captured post {i+1}")
                    else:
                        print(f"✗ Failed to capture post {i+1}")
                    
                    # Add delay between screenshots
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error processing URN {urn}: {e}")
                    continue

            self.save_to_csv(post_data)
            print(f"Successfully captured {len(post_data)} posts with screenshots")
            return post_data

        except Exception as e:
            print(f"Error during scraping: {e}")
            return []
        
        finally:
            driver.quit()

    def test_single_post_screenshot(self, urn):
        """Test screenshot functionality on a single post - useful for debugging."""
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(options=options)
        
        try:
            print("Logging into LinkedIn for test...")
            driver.get("https://linkedin.com/uas/login")
            
            wait = WebDriverWait(driver, 10)
            username = wait.until(EC.presence_of_element_located((By.ID, "username")))
            username.send_keys(self.email)
            
            pword = driver.find_element(By.ID, "password")
            pword.send_keys(self.password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            time.sleep(10)
            
            # Test the single post
            test_post_id = f"test_{urn}"
            screenshot_path = self.take_post_screenshot(driver, urn, test_post_id)
            
            if screenshot_path:
                print(f"✓ Test successful! Screenshot saved at: {screenshot_path}")
                return screenshot_path
            else:
                print("✗ Test failed - no screenshot captured")
                return None
                
        except Exception as e:
            print(f"Error during test: {e}")
            return None
        finally:
            driver.quit()

    def save_to_csv(self, post_data):
        """Save post data to CSV file."""
        if not post_data:
            print("No data to save")
            return

        df = pd.DataFrame(post_data)
        
        if os.path.exists(self.csv_file) and os.path.getsize(self.csv_file) > 0:
            existing_df = pd.read_csv(self.csv_file)
            df = df[~df['urn'].isin(existing_df['urn']) if 'urn' in existing_df.columns else True]
            if len(df) > 0:
                df.to_csv(self.csv_file, mode='a', header=False, index=False)
        else:
            df.to_csv(self.csv_file, index=False)
        
        print(f"Saved {len(df)} new posts to {self.csv_file}")

# Usage
if __name__ == "__main__":
    bot = LinkedInScreenshotHandler()
    posts = bot.fetch_posts_with_screenshots()