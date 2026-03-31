import re

def clean_wp_html(html_content):
    """
    Surgically cleans WordPress HTML before it is converted to Markdown.
    Handles shortcodes, Gutenberg wrappers, and layout noise.
    """
    if not html_content:
        return ""

    # 1. Strip Gutenberg Comment Wrappers (e.g., <!-- wp:paragraph -->)
    # This is often the first layer of noise.
    cleaned = re.sub(r'<!-- /?wp:.*? -->', '', html_content)

    # 2. Handle [caption] shortcodes
    # WordPress format: [caption id="..." align="..." width="..." caption="My Caption"]<img ... />[/caption]
    # We'll extract the img and the caption text.
    cleaned = re.sub(
        r'\[caption.*?\](.*?<img.*?>).*?caption="(.*?)".*?\[/caption\]',
        r'<figure>\1<figcaption>\2</figcaption></figure>',
        cleaned,
        flags=re.DOTALL
    )
    # Handle the simpler [caption] format where caption is outside the tag
    cleaned = re.sub(
        r'\[caption.*?\](.*?<img.*?>)\s*(.*?)\[/caption\]',
        r'<figure>\1<figcaption>\2</figcaption></figure>',
        cleaned,
        flags=re.DOTALL
    )

    # 3. Strip layout-only <div> tags but KEEP their content
    # Gutenberg and themes wrap everything in nested divs.
    cleaned = re.sub(r'<div[^>]*>', '', cleaned)
    cleaned = cleaned.replace('</div>', '')

    # 4. Clean up <span> tags but KEEP their content
    cleaned = re.sub(r'<span[^>]*>', '', cleaned)
    cleaned = cleaned.replace('</span>', '')

    # 5. Simple Embed handling (YouTube)
    # Convert [embed] links or raw links into Hugo youtube shortcodes
    youtube_regex = r'\[embed\]https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+)\[/embed\]'
    cleaned = re.sub(youtube_regex, r'{{< youtube \1 >}}', cleaned)
    
    # Handle raw youtube URLs that aren't inside tags (common in WP)
    raw_youtube_regex = r'^(https?://(?:www\.)?youtube\.com/watch\?v=([\w-]+))$'
    cleaned = re.sub(raw_youtube_regex, r'{{< youtube \2 >}}', cleaned, flags=re.MULTILINE)

    # 6. Tables: Remove inline styles and classes to help Markdownify
    cleaned = re.sub(r'<(table|tr|td|th)[^>]*>', r'<\1>', cleaned)

    return cleaned.strip()
