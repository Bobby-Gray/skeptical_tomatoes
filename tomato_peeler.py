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
            next_page_button = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]').get_attribute("innerHTML")
            self.reviews = {}
            while 'next hide' not in next_page_button:
                index = 1
                try:
                    index_review_len = int(review_table_len)
                    # next_page = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]')
                    while index <= index_review_len:
                        try:
                            review_profile_href = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']/div[1]/div/a'
                            review_star_score_path = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']/div[2]/div[1]/span[1]/span'
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
                            self.reviews.update({review_row_profile_href : [score]})
                            print({review_row_profile_href : [score]})
                            index += 1
                        except Exception as err:
                            print(err)
                            pass
                except Exception as err:
                    print(err)
                    pass
                driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]').click()
                driver.refresh()
                index_review_len = len(driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div'))
                index = 1
            else:
                pass
        return self.reviews
    
    def gather_audience_review_count(self):
        self.audience_reviews_dict = self.parse_and_print_audience_reviews_element_ids()
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        with webdriver.Chrome(options=op) as driver:
            for reviewer, score in self.audience_reviews_dict.items():
                print(f'Gathering audience review count from profile: {reviewer}')
                reviewer_s = str(reviewer)
                review_count = 0 
                try:
                    link_replace = reviewer_s.replace("/profiles/","/profiles/ratings/")
                    tv_link = link_replace + "/tv"
                    movie_link = link_replace + "/movie"
                    driver.get(tv_link)
                    tv_review_table = driver.find_element(By.XPATH, '//*[@id="profiles"]/div/div[3]').get_attribute("innerHTML")
                    tv_review_s = str(tv_review_table)
                    tv_review_count = tv_review_s.count('profile-rating reviewpresent')
                    review_count += tv_review_count
                    driver.get(movie_link)
                    movie_review_table = driver.find_element(By.XPATH, '//*[@id="profiles"]/div/div[3]').get_attribute("innerHTML")
                    movie_review_s = str(movie_review_table)
                    movie_review_count = movie_review_s.count('profile-rating reviewpresent')
                    review_count += movie_review_count
                except Exception as err:
                        print(err)
                        continue
                self.audience_reviews_dict.update({ reviewer : [score[0], review_count]})        
        print(f'self.audience_reviews_dict: {self.audience_reviews_dict}')
        return self.audience_reviews_dict
    
    def calc_review_ranges_from_audience_reviews_dict(self, audience_reviews_with_count):
        self.audience_reviews_dict_completed = audience_reviews_with_count
        one_review = 0
        one_review_count = 0
        two_to_ten_reviews = 0
        two_to_ten_reviews_count = 0
        eleven_plus_reviews = 0
        eleven_plus_reviews_count = 0  
        for context in self.audience_reviews_dict_completed.values():
            if context[1] <= 1:
                one_review += context[0]
                one_review_count += 1
            elif context[1] > 1 and context[1] < 11:
                two_to_ten_reviews += context[0]
                two_to_ten_reviews_count += 1
            elif context[1] >= 11:
                eleven_plus_reviews += context[0]
                eleven_plus_reviews_count +=1
            else:
                continue 
        one_review_avg = one_review / one_review_count
        two_to_ten_reviews_avg = two_to_ten_reviews / two_to_ten_reviews_count
        eleven_plus_reviews_avg = eleven_plus_reviews / eleven_plus_reviews_count
        print(f'{one_review_count} reviewers with only one review gave an average rating of {one_review_avg}.')
        print(f'{two_to_ten_reviews_count} reviewers with 2-10 reviews gave an average rating of {two_to_ten_reviews_avg}.')
        print(f'{eleven_plus_reviews_count} reviewers with 11+ reviews gave an average rating of {eleven_plus_reviews_avg}.')
    
tomato_peeler = TomatoPeeler()

result = tomato_peeler.generate_input_url()
print(result)

audience_reviews_url = tomato_peeler.generate_audience_reviews_input_url()
#print(audience_reviews_url)

response_text = tomato_peeler.get_url()
#print(response_text)

audience_reviews_response_text = tomato_peeler.get_audience_reviews_url()
#print(audience_reviews_response_text)

# Call the parse_and_print_element_ids method to parse and print element IDs
element_ids = tomato_peeler.parse_and_print_element_ids(response_text)
#print(element_ids)

# Call the parse_and_print_element_ids method to parse and print element IDs
audience_reviews = tomato_peeler.parse_and_print_audience_reviews_element_ids()
#print(audience_reviews)

# Call the parse_and_print_element_ids method to parse and print element IDs
audience_reviews_with_count = tomato_peeler.gather_audience_review_count()
#print(audience_reviews_with_count)

# Call the parse_and_print_element_ids method to parse and print element IDs
results = tomato_peeler.calc_review_ranges_from_audience_reviews_dict(audience_reviews_with_count)
print(results)
