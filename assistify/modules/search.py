"""
Web search functionality including Wikipedia, web search, and YouTube.
"""

import requests
import wikipedia
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
from config.settings import USER_AGENT, WEB_SEARCH_RESULTS, YOUTUBE_RESULTS, WIKIPEDIA_SENTENCES


class WikipediaSearch:
    """Wikipedia search functionality."""
    
    @staticmethod
    def get_summary(query):
        """
        Get Wikipedia summary for a query.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Wikipedia summary or error message
        """
        try:
            return wikipedia.summary(query, sentences=WIKIPEDIA_SENTENCES)
        except wikipedia.DisambiguationError as e:
            options = '\n- '.join(e.options[:5])
            return f"❓ Wikipedia ambiguous. Try being more specific. Some options:\n- {options}"
        except wikipedia.PageError:
            return "❌ Wikipedia: No page found."
        except Exception as e:
            return f"❌ Wikipedia error: {e}"


class WebSearch:
    """Web search using multiple search engines."""
    
    @staticmethod
    def search_duckduckgo(query, num_results=WEB_SEARCH_RESULTS):
        """Search using DuckDuckGo."""
        try:
            headers = {"User-Agent": USER_AGENT}
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                for result in soup.find_all('a', class_='result__a', limit=num_results):
                    title = result.get_text()
                    href = result.get('href')
                    if href:
                        results.append({'title': title, 'url': href})
                
                return results if results else None
            return None
        except Exception as e:
            print(f"DuckDuckGo search error: {e}")
            return None
    
    @staticmethod
    def _decode_bing_url(bing_url):
        """Decode Bing's wrapped URLs to get the actual URL."""
        try:
            import base64
            # Bing format: https://www.bing.com/ck/a?!&&p=XXXXX&...&u=aXXXX
            # The actual URL is base64 encoded in the 'u' parameter
            if 'u=' in bing_url:
                # Extract the base64 part after 'u='
                encoded_part = bing_url.split('u=')[1].split('&')[0]
                # Bing uses URL-safe base64 encoding
                # Add padding if needed
                encoded_part += '=' * (4 - len(encoded_part) % 4)
                decoded_bytes = base64.urlsafe_b64decode(encoded_part)
                actual_url = decoded_bytes.decode('utf-8')
                return actual_url
        except:
            pass
        return bing_url
    
    @staticmethod
    def search_bing(query, num_results=WEB_SEARCH_RESULTS):
        """Search using Bing with proper URL decoding and multiple user agents."""
        try:
            # Try with a simpler approach - use requests with cookies  
            session = requests.Session()
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9",
            })
            
            url = f"https://www.bing.com/search?q={quote_plus(query)}"
            print("[Bing] URL: " + url[:70])
            
            response = session.get(url, timeout=15)
            print("[Bing] Status: " + str(response.status_code))
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            print("[Bing] Searching...")
            
            # Find all li.b_algo elements
            result_items = soup.find_all('li', class_='b_algo')
            print("[Bing] Found: " + str(len(result_items)))
            
            for result in result_items:
                try:
                    title_tag = result.find('h2')
                    if not title_tag:
                        continue
                    
                    link_tag = title_tag.find('a') if title_tag else None
                    if not link_tag:
                        link_tag = result.find('a')
                    if not link_tag:
                        continue
                    
                    title = title_tag.get_text().strip()
                    bing_url = link_tag.get('href', "")
                    
                    if not title or not bing_url:
                        continue
                    
                    actual_url = WebSearch._decode_bing_url(bing_url)
                    
                    if not actual_url.startswith('http'):
                        actual_url = bing_url
                    
                    if any(r['url'] == actual_url for r in results):
                        continue
                    
                    results.append({'title': title, 'url': actual_url})
                    
                    if len(results) >= num_results:
                        break
                except:
                    pass
            
            print("[Bing] Got " + str(len(results)))
            return results if results else None
        
        except Exception as e:
            print("[Bing] Error: " + str(e))
            return None
    
    @staticmethod
    def search_brave(query, num_results=WEB_SEARCH_RESULTS):
        """Search using Brave."""
        try:
            headers = {"User-Agent": USER_AGENT}
            url = f"https://search.brave.com/search?q={quote_plus(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                for result in soup.find_all('div', class_='snippet', limit=num_results):
                    title_tag = result.find('span', class_='snippet-title')
                    link_tag = result.find_parent('a')
                    
                    if title_tag and link_tag:
                        title = title_tag.get_text()
                        url = link_tag.get('href')
                        if url and url.startswith('http'):
                            results.append({'title': title, 'url': url})
                
                return results if results else None
            return None
        except Exception as e:
            print(f"Brave search error: {e}")
            return None
    
    @staticmethod
    def get_results(query, num_results=WEB_SEARCH_RESULTS):
        """
        Get search results ONLY from Bing as the primary web search engine.
        
        Args:
            query (str): Search query
            num_results (int): Number of results (default 5)
            
        Returns:
            tuple: (results list, "Bing") or (None, None)
        """
        # Use Bing as the only web search engine
        results = WebSearch.search_bing(query, num_results)
        
        if results and len(results) > 0:
            print("[Web] Complete: Found " + str(len(results)) + " results from Bing")
            return results, "Bing"
        
        print("[Web] No results found for: " + query)
        return None, None


class YouTubeSearch:
    """YouTube search functionality."""
    
    @staticmethod
    def search(query, num=YOUTUBE_RESULTS):
        """
        Search YouTube with multiple fallback methods.
        
        Args:
            query (str): Search query
            num (int): Number of results
            
        Returns:
            list: List of videos with title and url
        """
        # Try youtubesearchpython library first
        try:
            from youtubesearchpython import VideosSearch
            search = VideosSearch(query, limit=num)
            result = search.result().get("result", [])
            
            if result:
                videos = []
                for v in result:
                    videos.append({
                        'title': v.get("title", "No title"),
                        'url': v.get("link", "")
                    })
                return videos
        except Exception as e:
            print(f"YouTube search library error: {e}")
        
        # Fallback to web scraping
        try:
            headers = {"User-Agent": USER_AGENT}
            q = quote_plus(query)
            response = requests.get(f"https://www.youtube.com/results?search_query={q}", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", response.text)
                seen = set()
                unique_ids = [x for x in video_ids if not (x in seen or seen.add(x))]
                
                videos = []
                for vid_id in unique_ids[:num]:
                    videos.append({
                        'title': f"Video: {vid_id}",
                        'url': f"https://www.youtube.com/watch?v={vid_id}"
                    })
                
                return videos if videos else None
            return None
        except Exception as e:
            print(f"YouTube fallback error: {e}")
            return None


class SearchManager:
    """Unified search manager coordinating all search types."""
    
    def __init__(self):
        self.wikipedia = WikipediaSearch()
        self.web = WebSearch()
        self.youtube = YouTubeSearch()
    
    def search_all(self, query):
        """
        Perform comprehensive search across all sources.
        
        Returns:
            dict: Dictionary with 'wikipedia', 'web', and 'youtube' results
        """
        return {
            'wikipedia': self.wikipedia.get_summary(query),
            'web': self.web.get_results(query),
            'youtube': self.youtube.search(query)
        }
