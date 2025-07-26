import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
import re
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
import html2text
from io import StringIO
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import logging
from typing import Dict, List, Any, Optional
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Universal Web Scraper",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.rate_limit = 5  # seconds between requests
        self.last_request_time = 0
        
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def check_robots_txt(self, url: str) -> bool:
        """Check robots.txt compliance"""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            return rp.can_fetch(self.session.headers['User-Agent'], url)
        except Exception:
            return True  # Allow if robots.txt cannot be checked
    
    def rate_limit_check(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def rotate_user_agent(self):
        """Rotate user agent"""
        import random
        self.session.headers['User-Agent'] = random.choice(self.user_agents)
    
    def fetch_with_requests(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch content using requests with retry logic"""
        for attempt in range(retries):
            try:
                self.rate_limit_check()
                self.rotate_user_agent()
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
        
        return None
    
    def fetch_with_selenium(self, url: str) -> Optional[str]:
        """Fetch content using Selenium for JavaScript-rendered pages"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            html = driver.page_source
            driver.quit()
            
            return html
            
        except (TimeoutException, WebDriverException) as e:
            logger.error(f"Selenium fetch failed: {e}")
            return None
    
    def extract_data(self, html: str, url: str) -> Dict[str, Any]:
        """Extract all data from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        data = {
            'text': self.extract_text(soup),
            'tables': self.extract_tables(soup),
            'links': self.extract_links(soup, url),
            'images': self.extract_images(soup, url),
            'metadata': self.extract_metadata(soup)
        }
        
        return data
    
    def extract_text(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract text content"""
        text_data = {}
        
        # Extract title
        title = soup.find('title')
        text_data['title'] = title.text.strip() if title else 'No title found'
        
        # Extract headings
        headings = []
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                headings.append(f"H{i}: {heading.text.strip()}")
        text_data['headings'] = '\n'.join(headings)
        
        # Extract paragraphs
        paragraphs = []
        for p in soup.find_all('p'):
            text = p.text.strip()
            if text:
                paragraphs.append(text)
        text_data['paragraphs'] = '\n\n'.join(paragraphs)
        
        # Extract all text using html2text
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        text_data['clean_text'] = h.handle(str(soup))
        
        return text_data
    
    def extract_tables(self, soup: BeautifulSoup) -> List[pd.DataFrame]:
        """Extract tables and convert to DataFrames"""
        tables = []
        
        for table in soup.find_all('table'):
            try:
                # Use pandas to parse table
                df = pd.read_html(str(table))[0]
                tables.append(df)
            except Exception as e:
                logger.warning(f"Failed to parse table: {e}")
                continue
        
        return tables
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'text': link.text.strip(),
                'url': absolute_url,
                'relative_url': href
            })
        
        return links
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all images"""
        images = []
        
        for img in soup.find_all('img', src=True):
            src = img['src']
            absolute_url = urljoin(base_url, src)
            
            images.append({
                'src': absolute_url,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        
        return images
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata"""
        metadata = {}
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                metadata[name] = content
        
        return metadata
    
    def scrape_url(self, url: str, use_selenium: bool = False) -> Optional[Dict[str, Any]]:
        """Main scraping method"""
        if not self.validate_url(url):
            raise ValueError("Invalid URL format")
        
        if not self.check_robots_txt(url):
            raise ValueError("Scraping not allowed by robots.txt")
        
        # Try requests first, then Selenium if needed
        html = None
        
        if not use_selenium:
            html = self.fetch_with_requests(url)
        
        if html is None:
            st.info("Switching to Selenium for JavaScript-rendered content...")
            html = self.fetch_with_selenium(url)
        
        if html is None:
            raise Exception("Failed to fetch content with both methods")
        
        return self.extract_data(html, url)

# Initialize session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'scraping_logs' not in st.session_state:
    st.session_state.scraping_logs = []

def add_log(message: str):
    """Add message to scraping logs"""
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.scraping_logs.append(f"[{timestamp}] {message}")

def filter_content(content: str, keywords: List[str]) -> str:
    """Filter content by keywords"""
    if not keywords:
        return content
    
    lines = content.split('\n')
    filtered_lines = []
    
    for line in lines:
        for keyword in keywords:
            if keyword.lower() in line.lower():
                filtered_lines.append(line)
                break
    
    return '\n'.join(filtered_lines)

def create_download_link(data: str, filename: str, mime_type: str = "text/plain") -> str:
    """Create download link for data"""
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'

def main():
    st.title("🕷️ Universal Web Scraper")
    st.markdown("*Scrape any website with customizable output and ethical safeguards*")
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # Rate limiting
    rate_limit = st.sidebar.slider("Rate Limit (seconds)", 1, 10, 5)
    
    # Force Selenium option
    force_selenium = st.sidebar.checkbox("Force Selenium (for JS-heavy sites)", False)
    
    # Filtering options
    st.sidebar.subheader("🔍 Content Filtering")
    filter_keywords = st.sidebar.text_input("Keywords (comma-separated)", "")
    keywords = [k.strip() for k in filter_keywords.split(",") if k.strip()]
    
    # Toggle sections
    st.sidebar.subheader("📋 Content Sections")
    show_text = st.sidebar.checkbox("Text Content", True)
    show_tables = st.sidebar.checkbox("Tables", True)
    show_links = st.sidebar.checkbox("Links", True)
    show_images = st.sidebar.checkbox("Images", True)
    show_metadata = st.sidebar.checkbox("Metadata", True)
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        url = st.text_input("🌐 Enter Website URL", placeholder="https://example.com")
    
    with col2:
        scrape_button = st.button("🚀 Scrape Website", type="primary")
    
    # URL validation
    if url and not url.startswith(('http://', 'https://')):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
        return
    
    # Scraping process
    if scrape_button and url:
        scraper = WebScraper()
        scraper.rate_limit = rate_limit
        
        # Progress tracking
        progress_container = st.container()
        logs_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        with logs_container:
            logs_placeholder = st.empty()
        
        try:
            # Initialize
            add_log("Initializing scraper...")
            progress_bar.progress(10)
            status_text.text("Validating URL...")
            
            # Validate URL
            if not scraper.validate_url(url):
                st.error("❌ Invalid URL format")
                return
            
            add_log("URL validation passed")
            progress_bar.progress(20)
            status_text.text("Checking robots.txt...")
            
            # Check robots.txt
            if not scraper.check_robots_txt(url):
                st.error("❌ Scraping not allowed by robots.txt")
                return
            
            add_log("Robots.txt check passed")
            progress_bar.progress(30)
            status_text.text("Fetching content...")
            
            # Scrape
            start_time = time.time()
            scraped_data = scraper.scrape_url(url, use_selenium=force_selenium)
            end_time = time.time()
            
            fetch_time = round(end_time - start_time, 2)
            
            add_log(f"Content fetched successfully in {fetch_time}s")
            progress_bar.progress(80)
            status_text.text("Processing data...")
            
            # Store in session state
            st.session_state.scraped_data = scraped_data
            st.session_state.scraped_data['fetch_time'] = fetch_time
            st.session_state.scraped_data['url'] = url
            
            add_log("Data processing completed")
            progress_bar.progress(100)
            status_text.text("✅ Scraping completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Scraping failed: {str(e)}")
            add_log(f"Error: {str(e)}")
        
        # Display logs
        if st.session_state.scraping_logs:
            with logs_placeholder:
                st.subheader("📊 Scraping Logs")
                for log in st.session_state.scraping_logs[-10:]:  # Show last 10 logs
                    st.text(log)
    
    # Display results
    if st.session_state.scraped_data:
        data = st.session_state.scraped_data
        
        # Metrics
        st.subheader("📈 Scraping Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Fetch Time", f"{data['fetch_time']}s")
        
        with col2:
            st.metric("Tables Found", len(data['tables']))
        
        with col3:
            st.metric("Links Found", len(data['links']))
        
        with col4:
            st.metric("Images Found", len(data['images']))
        
        # Results tabs
        tabs = []
        tab_names = []
        
        if show_text:
            tab_names.append("📝 Text")
        if show_tables:
            tab_names.append("📊 Tables")
        if show_links:
            tab_names.append("🔗 Links")
        if show_images:
            tab_names.append("🖼️ Images")
        if show_metadata:
            tab_names.append("📋 Metadata")
        
        if tab_names:
            tabs = st.tabs(tab_names)
            tab_index = 0
            
            # Text tab
            if show_text:
                with tabs[tab_index]:
                    st.subheader("Text Content")
                    
                    text_data = data['text']
                    
                    # Title
                    if text_data['title']:
                        st.markdown(f"**Title:** {text_data['title']}")
                    
                    # Headings
                    if text_data['headings']:
                        st.markdown("**Headings:**")
                        filtered_headings = filter_content(text_data['headings'], keywords)
                        st.text(filtered_headings)
                    
                    # Paragraphs
                    if text_data['paragraphs']:
                        st.markdown("**Paragraphs:**")
                        filtered_paragraphs = filter_content(text_data['paragraphs'], keywords)
                        st.text_area("", filtered_paragraphs, height=300)
                    
                    # Clean text
                    st.markdown("**Clean Text (Markdown):**")
                    filtered_clean = filter_content(text_data['clean_text'], keywords)
                    st.text_area("", filtered_clean, height=400)
                
                tab_index += 1
            
            # Tables tab
            if show_tables:
                with tabs[tab_index]:
                    st.subheader("Tables")
                    
                    if data['tables']:
                        for i, table in enumerate(data['tables']):
                            st.markdown(f"**Table {i+1}:**")
                            st.dataframe(table)
                    else:
                        st.info("No tables found on this page")
                
                tab_index += 1
            
            # Links tab
            if show_links:
                with tabs[tab_index]:
                    st.subheader("Links")
                    
                    if data['links']:
                        links_df = pd.DataFrame(data['links'])
                        
                        # Filter links
                        if keywords:
                            mask = links_df['text'].str.contains('|'.join(keywords), case=False, na=False)
                            links_df = links_df[mask]
                        
                        st.dataframe(links_df)
                    else:
                        st.info("No links found on this page")
                
                tab_index += 1
            
            # Images tab
            if show_images:
                with tabs[tab_index]:
                    st.subheader("Images")
                    
                    if data['images']:
                        images_df = pd.DataFrame(data['images'])
                        
                        # Filter images
                        if keywords:
                            mask = images_df['alt'].str.contains('|'.join(keywords), case=False, na=False)
                            images_df = images_df[mask]
                        
                        st.dataframe(images_df)
                    else:
                        st.info("No images found on this page")
                
                tab_index += 1
            
            # Metadata tab
            if show_metadata:
                with tabs[tab_index]:
                    st.subheader("Metadata")
                    
                    if data['metadata']:
                        metadata_df = pd.DataFrame(list(data['metadata'].items()), columns=['Name', 'Content'])
                        st.dataframe(metadata_df)
                    else:
                        st.info("No metadata found on this page")
        
        # Export options
        st.subheader("💾 Export Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📄 Export Text"):
                text_content = data['text']['clean_text']
                filtered_content = filter_content(text_content, keywords)
                st.download_button(
                    label="Download Text File",
                    data=filtered_content,
                    file_name=f"scraped_text_{int(time.time())}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("📊 Export Tables (CSV)") and data['tables']:
                # Combine all tables
                combined_csv = StringIO()
                for i, table in enumerate(data['tables']):
                    combined_csv.write(f"Table {i+1}\n")
                    table.to_csv(combined_csv, index=False)
                    combined_csv.write("\n\n")
                
                st.download_button(
                    label="Download CSV File",
                    data=combined_csv.getvalue(),
                    file_name=f"scraped_tables_{int(time.time())}.csv",
                    mime="text/csv"
                )
        
        with col3:
            if st.button("🔗 Export Links (JSON)"):
                links_json = json.dumps(data['links'], indent=2)
                st.download_button(
                    label="Download JSON File",
                    data=links_json,
                    file_name=f"scraped_links_{int(time.time())}.json",
                    mime="application/json"
                )
        
        with col4:
            if st.button("📋 Export All (JSON)"):
                # Create exportable data
                export_data = {
                    'url': data['url'],
                    'fetch_time': data['fetch_time'],
                    'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S"),
                    'text': data['text'],
                    'tables': [table.to_dict() for table in data['tables']],
                    'links': data['links'],
                    'images': data['images'],
                    'metadata': data['metadata']
                }
                
                export_json = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    label="Download Complete Data",
                    data=export_json,
                    file_name=f"scraped_data_{int(time.time())}.json",
                    mime="application/json"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with ethical scraping practices - respects robots.txt and implements rate limiting*")

if __name__ == "__main__":
    main()S