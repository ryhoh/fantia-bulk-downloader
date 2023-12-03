import argparse
import os
import time

import requests
from bs4 import BeautifulSoup


# Config
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                'Chrome/94.0.4606.61 Safari/537.36'
sleep_time = 2


# Get the html of the fanclub page
def get_fanclub_html(fanciub_id: int, page_number: int = 1) -> str:
    url = 'https://fantia.jp/fanclubs/%s/posts' % fanciub_id

    # Get the html with the user agent, session id, page number
    headers = {'User-Agent': user_agent}
    cookies = {'session_id': session_id}
    params = {'page': page_number}
    response = requests.get(url, headers=headers, cookies=cookies, params=params)
    time.sleep(sleep_time)
    return response.text

# Extract psot ids from the html
def extract_post_ids(html: str) -> list:
    soup = BeautifulSoup(html, 'lxml')
    post_ids = []

    # Find "post" class divs
    post_divs = soup.find_all('div', class_='post')

    # Extract post ids from the a tags in the divs
    for post_div in post_divs:
        post_id = post_div.find('a')['href'].split('/')[-1]
        post_ids.append(post_id)

    return post_ids

# Get the html of the post
def get_post_html(post_id: int) -> str:
    url = 'https://fantia.jp/posts/%s' % post_id

    # Get the html with the user agent, session id
    headers = {'User-Agent': user_agent}
    cookies = {'session_id': session_id}
    response = requests.get(url, headers=headers, cookies=cookies)
    time.sleep(sleep_time)
    return response.text

# Save the images in the post
def save_images(html: str, post_id: int) -> None:
    # Make save folder /posts/<post_id>
    if not os.path.exists('posts'):
        os.mkdir('posts')
    if not os.path.exists('posts/%s' % post_id):
        os.mkdir('posts/%s' % post_id)

    # Parse html
    soup = BeautifulSoup(html, 'lxml')

    # Find divs contains "post-thumbnail" class
    post_thumbnail_div = soup.find('div', class_='post-thumbnail')  # fixme need Selenium

    # Find "picture" tag in the div
    picture_tag = post_thumbnail_div.find('picture')

    # Find "img" tags in the "picture" tag
    img_tags = picture_tag.find_all('img')

    # Extract image urls from the img tags
    img_urls = []
    for img_tag in img_tags:
        img_urls.append(img_tag['src'])

    # Save the images
    for img_url in img_urls:
        # Get the image with the user agent, session id
        headers = {'User-Agent': user_agent}
        cookies = {'session_id': session_id}
        response = requests.get(img_url, headers=headers, cookies=cookies)

        # Save the image
        with open('posts/%s/%s' % (post_id, img_url.split('/')[-1]), 'wb') as f:
            f.write(response.content)
            print("[INFO] Thumbnail saved: " % img_url)
            time.sleep(sleep_time)
    

if __name__ == '__main__':
    # Parse arguments
    # -u <fanclub_id>
    # -s <session_id>
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--user', type=str, help='fanclub id')
    parser.add_argument('-s', '--session', type=str, help='session id')
    args = parser.parse_args()
    fanclub_id = args.user
    session_id = args.session

    # Get the html of the fanclub page
    html = get_fanclub_html(fanclub_id)
    
    # Extract post ids from the html
    post_ids = extract_post_ids(html)
    
    # Get the html of the post
    for post_id in post_ids:
        post_html = get_post_html(post_id)

        # [debug] save html
        with open('posts/%s/%s.html' % (post_id, post_id), 'wb') as f:
            f.write(bytes(post_html, encoding='utf-8'))

        save_images(post_html, post_id)
        break

