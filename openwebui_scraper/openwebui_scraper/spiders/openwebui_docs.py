import scrapy
import os
from urllib.parse import urljoin, urlparse


class OpenwebuiDocsSpider(scrapy.Spider):
    name = "openwebui_docs"
    allowed_domains = ["docs.openwebui.com"]
    start_urls = ["https://docs.openwebui.com"]

    def parse(self, response):
        # Extract page title
        title = response.css('title::text').get() or response.css('h1::text').get() or 'No Title'

        # OPTION 1: Save FULL HTML (preserves all formatting, CSS, images)
        full_html = response.text

        # OPTION 2: Extract main content HTML (preserves structure but removes nav/header)
        # Try different selectors for main content area
        main_content_selectors = [
            'main',
            '.content',
            '.markdown',
            'article',
            '.doc-content',
            '.documentation-content',
            '#content',
            '.main-content'
        ]

        content_html = None
        for selector in main_content_selectors:
            content_element = response.css(selector)
            if content_element:
                content_html = content_element.get()  # .get() returns HTML, .getall() returns list
                break

        # Fallback to body if no main content found
        if not content_html:
            content_html = response.css('body').get()

        # Create filename from URL path
        parsed_url = urlparse(response.url)
        path = parsed_url.path.strip('/')
        if not path:
            path = 'index'

        # Replace slashes with underscores and add .html extension
        filename = path.replace('/', '_') + '.html'

        # Yield the extracted data (choose one option)
        yield {
            'url': response.url,
            'title': title,
            'full_html': full_html,           # OPTION 1: Full page HTML
            'content_html': content_html,    # OPTION 2: Main content HTML only
            'filename': filename
        }

        # Follow all documentation links
        doc_links = response.css('a::attr(href)').getall()
        for link in doc_links:
            # Convert relative URLs to absolute
            absolute_url = urljoin(response.url, link)

            # Only follow links within docs.openwebui.com
            if urlparse(absolute_url).netloc == 'docs.openwebui.com':
                # Avoid duplicate requests and external links
                if not absolute_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.js')):
                    yield response.follow(absolute_url, self.parse)
