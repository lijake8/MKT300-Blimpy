from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
import nltk
from nltk.corpus import stopwords

# make a pandas database from the set
def get_review_summary(result_set):
    rev_dict = {'Rating': [],
                'Time': [],
                'Text' : []}
    for result in result_set:
        review_rate = result.find('span', class_='ODSEW-ShBeI-H1e3jb')["aria-label"]
        review_time = result.find('span',class_='ODSEW-ShBeI-RgZmSc-date').text
        review_text = result.find('span',class_='ODSEW-ShBeI-text').text
        rev_dict['Rating'].append(review_rate)
        rev_dict['Time'].append(review_time)
        rev_dict['Text'].append(review_text)
    return(pd.DataFrame(rev_dict))

# return the most used words among all reviews
def get_most_common_phrases(dataframe):
    # create master list for all words
    master_list = []

    # get the review portion from database
    text_only = dataframe['Text']
    for review in text_only:
        # split long sentence string into individual strings and add to dict
        word_list = re.findall(r'[^\s!,.?":;0-9]+', review)
        master_list.extend(word_list)

    # count frequencies
    # make stoplist of common english words to be ignored
    ignore_list = stopwords.words('english')
    ignore_list.append('...')
    ignore_list.append('burger')
    ignore_list.append('burgers')
    ignore_list.append('place')
    ignore_list.append('food')
    ignore_list.append('ann')
    ignore_list.append('arbor')
    
    # use nltk library to find frequencies
    clean_master_list = master_list[:]
    for word in master_list:
        if word.lower() in ignore_list:
            clean_master_list.remove(word)
    freq = nltk.FreqDist(clean_master_list)
    # for key,val in freq.items():
    #     print(str(key) + ':' + str(val))

    # use matplotlib to generate plot
    freq.plot(20, cumulative=False)


def main():
    # needed to stop chrome window closing immediately
    chr_options = Options()
    chr_options.add_experimental_option("detach", True)

    # set driver, hardcode URL for blimpy's
    driver = webdriver.Chrome(options=chr_options)
    url = "https://www.google.com/maps/place/Krazy+Jim's+Blimpy+Burger/@42.2718698,-83.7305383,15z/data=!4m5!3m4!1s0x883cae3ceea6a2db:0x1d4f4a6f9d2cc930!8m2!3d42.279399!4d-83.750068"
    driver.get(url)

    # using hardcoded classname for the reviews hyperlink, find the link and click it
    try:
        driver.find_element(By.CLASS_NAME, "Yr7JMd-pane-hSRGPd").click() 
    except Exception:
        response = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Check if there are any paid ads and avoid them
        if response.find_all('span', {'class': 'ARktye-badge'}):
            ad_count = len(response.find_all('span', {'class': 'ARktye-badge'}))
            li = driver.find_elements(By.CLASS_NAME, "a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd")
            li[ad_count].click()
        else:
            driver.find_element(By.CLASS_NAME, "a4gq8e-aVTXAb-haAclf-jRmmHf-hSRGPd").click()
            time.sleep(5)
        driver.find_element(By.CLASS_NAME, "Yr7JMd-pane-hSRGPd").click()

    # add a (generous) pause to ensure page loads before moving on
    time.sleep(5)

    # find scroll object
    scrollable_div = driver.find_element(by=By.CSS_SELECTOR, value='#pane > div > div.Yr7JMd-pane-content.cYB2Ge-oHo7ed > div > div > div.siAUzd-neVct.section-scrollbox.cYB2Ge-oHo7ed.cYB2Ge-ti6hGc')
    
    # scroll an arbitrary number of times, each time loads 10 more reviews
    for i in range(0, 100): #100 for 1000 reviews
        driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
        time.sleep(1)

    # get reviews from page
    response = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = response.find_all('div', class_='ODSEW-ShBeI NIyLF-haAclf gm2-body-2')
    
    # make it into a dataframe to be easier to work with
    dataframe = get_review_summary(reviews)

    get_most_common_phrases(dataframe)

if __name__ == "__main__":
    main()
