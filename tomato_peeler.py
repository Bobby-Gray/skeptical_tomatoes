from bs4 import BeautifulSoup
import json 
import requests
import pandas   
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TomatoPeeler:
    def __init__(self):
        self.tv_or_movie = input("Enter tv or movie: ") or "tv"
        if self.tv_or_movie == "tv":
            self.property = input("Enter tv series name as it appears in the RottenTomatoes url. e.g., 'star_wars_ahsoka': ") or "star_wars_ahsoka"
            self.season = input("Enter season of tv series as 's' + season number. e.g., 's01': ") or "s01"
            self.entity_uri = "/tv/" + self.property + "/" + self.season

        elif self.tv_or_movie == "movie":
            self.property = input("Enter movie name as it appears in the RottenTomatoes url. e.g., 'star_wars_the_last_jedi': ") or "star_wars_the_last_jedi"
            self.entity_uri = "/m/" + self.property

        else:
            print("Uh oh! Something broke w/ input.")
            exit

    def generate_input_url(self):
        self.base_url = "https://rottentomatoes.com"
        self.url = self.base_url + self.entity_uri
        return self.url
    
    def generate_audience_reviews_input_url(self):
        self.audience_reviews_url = self.generate_input_url() + "/reviews?type=user"
        return self.audience_reviews_url
        
    def get_url(self):
        url = self.generate_input_url()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}  # Optional headers
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to make GET request. Status code: {response.status_code}"

    def get_audience_reviews_url(self):
        url = self.generate_audience_reviews_input_url()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}  # Optional headers
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return f"Failed to make GET request. Status code: {response.status_code}"
    
    def parse_and_print_element_ids(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        element_ids = soup.find_all(id=True)
        
        if element_ids:
            print("Element IDs found in the response:")
            for element in element_ids:
                #print(element['id'])
                if "scoreDetails" in element['id']:
                    score_details = json.loads(element.contents[0])
                    #print(json.dumps(score_details, indent=4, sort_keys=True))
                    audience_score_all = score_details['modal']['audienceScoreAll']
                    critics_score_all = score_details['modal']['tomatometerScoreAll']
                    audience_average_rating = audience_score_all.get('averageRating')
                    audience_disliked_count = audience_score_all.get('notLikedCount')
                    audience_liked_count = audience_score_all.get('likedCount')
                    audience_score = audience_score_all.get('value')
                    self.audience_total = int(audience_liked_count + audience_disliked_count)
                    critics_average_rating = critics_score_all.get('averageRating')
                    critics_disliked_count = critics_score_all.get('notLikedCount')
                    critics_liked_count = critics_score_all.get('likedCount')
                    critics_score = critics_score_all.get('value')
                    print(f'audience_score: {audience_score}')
                    print(f'audience_average_rating: {audience_average_rating}')
                    print(f'audience_disliked_count: {audience_disliked_count}')
                    print(f'audience_liked_count: {audience_liked_count}')
                    print(f'audience_total: {self.audience_total}')
                    print(f'critics_score: {critics_score}')
                    print(f'critics_average_rating: {critics_average_rating}')
                    print(f'critics_disliked_count: {critics_disliked_count}')
                    print(f'critics_liked_count: {critics_liked_count}')
        else:
            print("No element IDs found in the response.")
        return self.audience_total

    def parse_and_print_audience_reviews_element_ids(self):
        link = self.generate_audience_reviews_input_url()
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        with webdriver.Chrome(options=op) as driver:
            driver.get(link)
            review_table_len = len(driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div'))
            print(f'review_table_len: {review_table_len}')
            next_page_button = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]').get_attribute("innerHTML")
            print(f'next_page_button: {next_page_button}')
            reviews = {}
            while 'next hide' not in next_page_button:
                index = 1
                index_review_len = int(review_table_len)
                # next_page = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]')
                while index <= index_review_len:
                    review_table_xpath = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']'
                    review_profile_href = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']/div[1]/div/a'
                    review_star_score_path = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']/div[2]/div[1]/span[1]/span'
                    review_row_xpath = driver.find_element(By.XPATH, review_table_xpath).get_attribute("innerHTML")
                    review_row_profile_href = driver.find_element(By.XPATH, review_profile_href).get_attribute("href")
                    review_star_score = driver.find_element(By.XPATH, review_star_score_path).get_attribute("innerHTML")
                    review_star_score1 = review_star_score.replace('<span class="',"")
                    review_star_score2 = review_star_score1.replace('"></span>',"")
                    review_star_score3 = review_star_score2.split(" ")
                    score = 0
                    for score_stars in review_star_score3:
                        if "filled" in score_stars:
                            score += 1
                        elif "star-display__half" in str(score_stars):
                            score += .5
                        else:
                            continue
                    reviews.update({review_row_profile_href : score})
                    index += 1
                driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]').click()
                time.sleep(1)
                driver.refresh()
                review_table_next = len(driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div'))
                index = int(review_table_next)
                print(f'index2: {str(index)}')
        print(f'review_table: {reviews}')


        ### SCRATCHPAD
            # prev_page = '//*[@id="reviews"]/div[3]/rt-button[1]'
            # next_page = '//*[@id="reviews"]/div[3]/rt-button[2]'

            # review_table_xpath = driver.find_element(By.XPATH, '//*[@id="reviews"]/div[2]').get_attribute("innerHTML")

        #     datalist = []
        #     show_more = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"#g-cases-by-state button[class^='svelte']")))
        #     driver.execute_script("arguments[0].click();",show_more)

        #     for elem in WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,"#g-cases-by-state table[class^='svelte'] tr"))):
        #         data = [item.text for item in elem.find_elements_by_css_selector("th,td")]
        #         datalist.append(data)

        # df = pandas.DataFrame(datalist)
        # print(df)
        # soup = BeautifulSoup(audience_reviews_response_text, 'html.parser')
        # element_ids = soup.find_all(id=True)
        # audience_count = self.audience_total
        # if element_ids:
        #     print("Element IDs found in the response:")
        #     for element in element_ids:
        #         print(element['id'])
        #         profiles = {}
        #         index = 0
        #         #while index < 40:
        #         if "reviews" in element['id']:
        #             #print(element)
        #             reviews = soup.find_all("div", {"class": "audience-review-row"})
        #             prevnext = soup.find("div", {"class": "prev-next-paging__wrapper"})
        #             prevnext1 = prevnext.find("rt-button", {"class": "next hide"})
        #             prevnext2 = prevnext1.click("Next")
        #             print(f'PAGING: {prevnext}')
        #             print(f'prevnext1: {prevnext1}')
        #             print(f'prevnext2: {prevnext2}')
        #             #prevnext1.click()
        #             for review in reviews:
        #                 score = 0
        #                 #print(f'each: {review}')
        #                 base_url = "https://rottentomatoes.com"
        #                 profile = review.a['href']
        #                 score_meta = review.find("span", {"class": 'star-display'})
        #                 for score_stars in score_meta:
        #                     #print(f'score_stars: {score_stars}')
        #                     if "filled" in str(score_stars):
        #                         score += 1
        #                     elif "star-display__half" in str(score_stars):
        #                         score += .5
        #                     else:
        #                         pass
        #                 #print(f'score_meta: {score_meta}')
                        
        #                 profiles.update({base_url + profile: score})
        #                 #profiles.append(score)
        #                 #print(f'score: {score}')
        #                 #print(f'profile: {profile}')
        #                 index += 1
        #                 #print(f'profile: {profile}') 
        #             return profiles, index, prevnext                        


        #                     # profile_id = str(review['a href'])
        #                     # print(f'profile_id: {profile_id}')

                        
        #                     # try:
        #                     #     # Go to page 2
        #                     #     next_link = browser.find_element_by_xpath('//*[@title="Go to page 2"]')
        #                     #     next_link.click()
        #                     #     index = 0

        #                     #     # update html and soup
        #                     #     html = browser.page_source
        #                     #     soup = BeautifulSoup(html, "html.parser")

        #                     #     time.sleep(30)
        #                     # except NoSuchElementException:
        #                     #     rows_remaining = False
        # else:
        #     print("No element IDs found in the response.")
        # print(profiles)
        # print(index)


tomato_peeler = TomatoPeeler()

result = tomato_peeler.generate_input_url()
print(result)

audience_reviews_url = tomato_peeler.generate_audience_reviews_input_url()
print(audience_reviews_url)

response_text = tomato_peeler.get_url()
#print(response_text)

audience_reviews_response_text = tomato_peeler.get_audience_reviews_url()
print(audience_reviews_response_text)

# Call the parse_and_print_element_ids method to parse and print element IDs
element_ids = tomato_peeler.parse_and_print_element_ids(response_text)
print(element_ids)

# Call the parse_and_print_element_ids method to parse and print element IDs
audience_reviews_element_ids = tomato_peeler.parse_and_print_audience_reviews_element_ids()
print(audience_reviews_element_ids)
