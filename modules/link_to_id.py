import re

def url_to_mediaid(url):
    def extract_shortcode(url):
        # Use regex to extract the shortcode from the URL
        match = re.search(r'/(reel|p)/([a-zA-Z0-9_-]+)', url)
        if match:
            return match.group(2)
        return None

    def shortcode_to_mediaid(shortcode):
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
        mediaid = 0

        for letter in shortcode:
            mediaid = (mediaid * 64) + alphabet.index(letter)

        return mediaid
    shortcode = extract_shortcode(url)
    if shortcode:
        return shortcode_to_mediaid(shortcode)
    else:
        return None


# Example usage
urls = [
    "https://www.instagram.com/reel/DBGl4UYSP6j/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA==",
    "https://www.instagram.com/p/DA1fQIguJ2W",
    "https://www.instagram.com/reel/C4bLPDRL1Hv"
]

# for url in urls:
#     media_id = url_to_mediaid(url)
#     print(f"Media ID for {url}: {media_id}")