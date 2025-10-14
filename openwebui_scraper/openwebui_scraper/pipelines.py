# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os


class OpenwebuiScraperPipeline:
    def __init__(self):
        # Create output directory
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
        os.makedirs(self.output_dir, exist_ok=True)

    def process_item(self, item, spider):
        # Choose which HTML version to save
        # OPTION 1: Save FULL HTML (preserves all original formatting, CSS, images)
        if 'full_html' in item and item['full_html']:
            html_content = item['full_html']

        # OPTION 2: Save main content HTML with basic wrapper (preserves content structure)
        elif 'content_html' in item and item['content_html']:
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{item['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #fff;
        }}
        .content {{
            max-width: 1200px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="content">
        {item['content_html']}
    </div>
    <div style="margin-top: 40px; padding: 20px; background: #f5f5f5; border-radius: 8px; font-size: 0.9em; color: #666;">
        <strong>Source:</strong> <a href="{item['url']}" target="_blank">{item['url']}</a>
    </div>
</body>
</html>"""

        # Fallback: Create basic HTML from text content (original behavior)
        else:
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{item['title']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .content {{
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <h1>{item['title']}</h1>
    <div class="meta">
        <strong>Source:</strong> <a href="{item['url']}" target="_blank">{item['url']}</a>
    </div>
    <div class="content">
        {item.get('content', 'No content extracted')}
    </div>
</body>
</html>"""
    <div class="meta">
        <strong>Source:</strong> <a href="{item['url']}" target="_blank">{item['url']}</a>
    </div>
    <div class="content">
        {item['content']}
    </div>
</body>
</html>"""

        # Save to file
        filepath = os.path.join(self.output_dir, item['filename'])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        spider.logger.info(f"Saved page: {item['filename']} - {item['title']}")

        return item
