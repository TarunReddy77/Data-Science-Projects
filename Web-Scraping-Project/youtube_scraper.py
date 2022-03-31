from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv, os, shutil, requests

def count_to_int(count):
    # 'K' in youbtube's view count means 1,000
    if count[-1] == 'K':
        count = int(float(''.join(count[:-1].split(','))) * 10 ** 3)
    # 'M' in youbtube's view count means 1,000,000
    elif count[-1] == 'M':
        count = int(float(''.join(count[:-1].split(','))) * 10 ** 6)
    else:
        count = int(float(''.join(count.split(','))))
    return count

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def scrape_videos_info(category, channel_name, videos_url):
    most_popular_url = videos_url + '?view=0&sort=p&flow=grid'
    driver.get(most_popular_url)

    wait.until(presence((By.ID,"video-title")))
    elements = driver.find_elements_by_id("video-title")

    while len(elements) < 50:
        driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
        wait.until(presence((By.ID,"video-title")))
        elements.extend(driver.find_elements_by_id("video-title"))
        elements = unique(elements)
        
    video_links = [element.get_attribute('href') for element in elements][:50]

    filename = r"C:\Users\lenovo\Desktop\Python Scripts\Top Channels\{}\{}.csv".format(category, channel_name)
    fields = ['rank', 'title', 'date', 'views', 'likes', 'dislikes', 'like_dislike_ratio', 'video_link']
        
    with open(filename, 'w', encoding = 'utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)

        for rank, link in enumerate(video_links[:5], 1):
            driver.get(link)

            wait.until(presence((By.CLASS_NAME,"ytd-video-primary-info-renderer")))
            info_str = driver.find_element_by_class_name("ytd-video-primary-info-renderer").text
            info_list = info_str.split('\n')
            info_list = [item for item in info_list if item not in ['SAVE', 'SHARE']]
            dislikes = info_list.pop(-1)
            likes = info_list.pop(-1)
            views_and_date = info_list.pop(-1)
            title = ' '.join(info_list)
            video_link = video_links[rank-1]
            
            if 'views' in views_and_date:
                items = views_and_date.split('views')
                views = int(float(''.join(items[0].strip().split(','))))
                date = 'Not Mentioned' if not items[1] else items[1]

            else:
                views = 'Not Mentioned'
                date = views_and_date

            if likes == 'LIKE':
                likes = 'Not Mentioned'

            if dislikes == 'DISLIKE':
                dislikes = 'Not Mentioned'

            like_dislike_ratio = 'Not Applicable'

            if likes != 'Not Mentioned':
                int_likes = count_to_int(likes)
                int_dislikes = count_to_int(dislikes)
                like_dislike_ratio = round(int_likes / int_dislikes, 2)

            row = [rank, title, date, views, likes, dislikes, like_dislike_ratio, video_link]
            csvwriter.writerow(row)
            # print(f'{title = }')
            # print(f'{date = }')
            # print(f'{views = }')
            # print(f'{likes = }')
            # print(f'{dislikes = }')
            # print(f'{like_dislike_ratio = }')

driver = webdriver.Chrome(r'C:\Program Files (x86)\chromedriver.exe')
# driver.maximize_window()

wait = WebDriverWait(driver, 100)
presence = EC.presence_of_element_located
visible = EC.visibility_of_element_located

url = 'https://blog.hubspot.com/marketing/best-youtube-channels'
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

categories = soup.find_all('div', class_ = 'hsg-featured-snippet')
category_names = [category.text for category in categories]
category_names = ['Educational', 'Cooking', 'Fitness and Workout', 'Yoga', 'History', 'Science', 'News', 'Music', 'Comedy', 'Travel']

for category, category_name in zip(categories, category_names):  # Modified
    dir = r"C:\Users\lenovo\Desktop\Python Scripts\Top Channels\{}".format(category_name)
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)

    channels = category.find_all('a')
    channel_attrs = []
    for rank, channel in enumerate(channels, 1):
        channel_url = channel['href']

        driver.get(channel_url)
        wait.until(presence((By.ID,"subscriber-count")))
        count = driver.find_element_by_id("subscriber-count").text.split()[0]

        wait.until(presence((By.CLASS_NAME,"tp-yt-paper-tab")))
        elems = driver.find_elements_by_class_name("tp-yt-paper-tab")
        videos_button = elems[1]
        videos_button.click()

        videos_url = driver.current_url
        channel_name = channel.text
        scrape_videos_info(category_name, channel_name, videos_url)

        channel_attrs.append([rank, channel_name, count, channel_url])

    channel_attrs = sorted(channel_attrs, key = lambda channel : count_to_int(channel[2]), reverse = True)

    filename = r"C:\Users\lenovo\Desktop\Python Scripts\Top Channels\{}.csv".format(category_name)
    fields = ['rank', 'channel', 'subscibers', 'url']
        
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for item in channel_attrs:
            csvwriter.writerow(item)
