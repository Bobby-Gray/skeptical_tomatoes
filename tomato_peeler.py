from bs4 import BeautifulSoup
import json 
import pprint
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
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
            self.response_text = response.text
            return self.response_text
        else:
            return f"Failed to make GET request. Status code: {response.status_code}"

    def get_audience_reviews_url(self):
        url = self.generate_audience_reviews_input_url()
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}  # Optional headers
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.audience_response_text = response.text
            return self.audience_response_text
        else:
            return f"Failed to make GET request. Status code: {response.status_code}"
    
    def parse_and_print_score_elements(self):
        soup = BeautifulSoup(self.get_url(), 'html.parser')
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
                    audience_rating_total = int(audience_liked_count + audience_disliked_count)
                    audience_review_count = audience_score_all.get('reviewCount')
                    critics_average_rating = critics_score_all.get('averageRating')
                    critics_disliked_count = critics_score_all.get('notLikedCount')
                    critics_liked_count = critics_score_all.get('likedCount')
                    critics_score = critics_score_all.get('value')
                    self.published_scores = {'audience_score:': audience_score,
                                        'audience_review_count:': audience_review_count, 
                                        'audience_average_rating:': audience_average_rating,
                                        'audience_disliked_count:': audience_disliked_count,
                                        'audience_liked_count:': audience_liked_count,
                                        'audience_rating_total:': audience_rating_total,
                                        'critics_score:': critics_score,
                                        'critics_average_rating:': critics_average_rating,
                                        'critics_disliked_count:': critics_disliked_count,
                                        'critics_liked_count': critics_liked_count}
                    pprint.pprint(f'published_scores: {self.published_scores}')
                    return self.published_scores
        else:
            print("No element IDs found in the response.")

    def parse_audience_review_table(self):
        link = self.generate_audience_reviews_input_url()
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        with webdriver.Chrome(options=op) as driver:
            driver.get(link)
            errors = [NoSuchElementException, StaleElementReferenceException]
            wait = WebDriverWait(driver, timeout=2, poll_frequency=.2, ignored_exceptions=errors)
            self.reviews = {}
            index = 1
            review_table = driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div')
            review_table_len = len(review_table)
            outer_tries = 3
            while outer_tries:
                try:
                    inner_tries = 3
                    index_review_len = int(review_table_len)
                    while index <= index_review_len:
                        try:
                            inner_outer_tries = 3
                            review_profile_href = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']/div[1]/div/a'
                            review_star_score_path = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index) + ']/div[2]/div[1]/span[1]/span'
                            review_row_profile_h = driver.find_element(By.XPATH, review_profile_href)
                            review_row_profile_href = str(wait.until(lambda d : review_row_profile_h.get_attribute("href") or True))
                            review_star_s = driver.find_element(By.XPATH, review_star_score_path)
                            review_star_score = str(wait.until(lambda d : review_star_s.get_attribute("innerHTML") or True))
                            review_star_score1 = review_star_score.replace('<span class="',"")
                            review_star_score2 = review_star_score1.replace('"></span>',"")
                            review_star_score3 = review_star_score2.split(" ")
                            score = float(0)
                            for score_stars in review_star_score3:
                                if "filled" in str(score_stars):
                                    score += float(1)
                                elif "star-display__half" in str(score_stars):
                                    score += float(.5)
                                else:
                                    pass
                            self.reviews.update({review_row_profile_href : [score]})
                            print({review_row_profile_href : [score]})
                            index += 1
                        except Exception as err:
                            print(err)
                            inner_tries -= 1
                            if inner_tries:
                                continue
                            else: 
                                break
                    next_page = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]')
                    wait.until(lambda d : next_page.click() or True)
                    time.sleep(3)
                    index_review_l = driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div')
                    index_review_len = len(index_review_l)
                    next_page_b = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]')
                    next_page_button = wait.until(lambda d : next_page_b.get_attribute("innerHTML") or True)
                    index_review_row = '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index_review_len) + ']/div[1]/div/a'
                    next_review_row_p = driver.find_element(By.XPATH, index_review_row)
                    next_review_row_profile = str(wait.until(lambda d : next_review_row_p.get_attribute("href") or True))
                    reviews_len = len(self.reviews)
                    print(f'next review row profile: {next_review_row_profile} table_len: {reviews_len}')
                    if next_review_row_profile in self.reviews.keys():
                        inner_outer_tries -= 1
                        if "next hide" in str(next_page_button):
                            print(f'Next page button hidden: {next_page_button}')
                            inner_tries = 0
                            outer_tries = 0
                            break
                        if inner_outer_tries:
                            index = 1
                            continue
                        else:
                            break
                    else:
                        index = 1
                    
                except Exception as err:
                    print(err)
                    outer_tries -= 1
                    continue
            else:
                outer_tries -= 1
        driver.quit()
        return self.reviews
    
    def gather_audience_review_count(self):
        self.audience_reviews_dict = self.reviews
        counter = 1
        total_count = len(self.audience_reviews_dict.items())
        uas = []
        ua_url = "https://raw.githubusercontent.com/tmxkn1/UpdatedUserAgents/master/useragents.json"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}  # Optional headers
        response = requests.get(ua_url, headers=headers)
        ua_list = json.loads(response.text)
        chrome_list = ua_list.get('chrome')
        firefox_list = ua_list.get('firefox')
        for ua in chrome_list.values():
            uas.append(ua)
        for ua in firefox_list.values():
            uas.append(ua)
        for reviewer, score in self.audience_reviews_dict.items():
            tries = 3
            print(f'Gathering review count for profile: {reviewer} \n count: {counter}/{total_count}')
            reviewer_s = str(reviewer)
            review_count = 0 
            op = webdriver.ChromeOptions()
            op.add_argument('headless')
            with webdriver.Chrome(options=op) as driver:
                errors = [NoSuchElementException, StaleElementReferenceException]
                wait = WebDriverWait(driver, timeout=2, poll_frequency=.2, ignored_exceptions=errors)
                try:
                    link_replace = reviewer_s.replace("/profiles/","/profiles/ratings/")
                    tv_link = link_replace + "/tv"
                    movie_link = link_replace + "/movie"
                    counter += 1
                    random_ua = str(random.choice(uas))
                    driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random_ua})
                    print(f'User Agent: {driver.execute_script("return navigator.userAgent;")}')
                    driver.get(tv_link)
                    tv_table = '//*[@id="profiles"]/div/div[3]'
                    tv_review_table = driver.find_element(By.XPATH, tv_table)                                                 
                    tv_review_s = str(wait.until(lambda d : tv_review_table.get_attribute("innerHTML") or True))
                    tv_review_count = tv_review_s.count('profile-rating reviewpresent')
                    print(f'tv review count: {tv_review_count}') 
                    if tv_review_count:
                        review_count += tv_review_count
                    driver.get(movie_link)
                    movie_table = '//*[@id="profiles"]/div/div[3]'
                    movie_review_table = driver.find_element(By.XPATH, movie_table)
                    movie_review_s = str(wait.until(lambda d : movie_review_table.get_attribute("innerHTML") or True))
                    movie_review_count = movie_review_s.count('profile-rating reviewpresent') 
                    print(f'movie review count: {movie_review_count}')
                    if movie_review_count:
                        review_count += movie_review_count
                    self.audience_reviews_dict.update({ reviewer : [score[0], review_count]})
                    entry = { reviewer : [score[0], review_count]}
                    pprint.pprint(f'review count update: {entry}')
                    driver.close()
                except Exception as err:
                        print(err)
                        if tries:
                            tries -= 1
                            driver.close()
                            continue
                        else:
                            driver.close()
                            break      
        driver.quit()
        return self.audience_reviews_dict
    
    def calc_review_ranges_from_audience_reviews_dict(self):
        self.audience_reviews_dict_completed = self.audience_reviews_dict
        one_review = 0
        one_review_count = 0
        two_to_nine_reviews = 0
        two_to_nine_reviews_count = 0
        ten_to_nineteen_reviews = 0
        ten_to_nineteen_reviews_count = 0
        twenty_plus_reviews = 0 
        twenty_plus_reviews_count = 0
        try:
            for prof, context in self.audience_reviews_dict_completed.items():
                if context[1] >= 20:
                    twenty_plus_reviews += context[0]
                    twenty_plus_reviews_count += 1
                    continue
                else:
                    if 10 <= context[1] < 20:
                        ten_to_nineteen_reviews += context[0]
                        ten_to_nineteen_reviews_count += 1
                        continue
                    else:
                        if 1 < context[1] < 10:
                            two_to_nine_reviews += context[0]
                            two_to_nine_reviews_count += 1
                            continue
                        else:
                            if 0 < context[1] <= 1:
                                one_review += context[0]
                                one_review_count += 1
                            else:
                                print(f'audience_reviews_dict_completed loop logic borked for {prof, context}')
                                continue
        except Exception as err:
            print(err)
            print(f'ie exception error for {prof, context}')
            pass    
        try: 
            one_review_avg = str(round((round(one_review / one_review_count, 3) * 20), 2)) + "%"
        except ZeroDivisionError:
            one_review_avg = 0
            pass
        try:
            two_to_nine_reviews_avg = str(round((round(two_to_nine_reviews / two_to_nine_reviews_count, 3) * 20), 2)) + "%"
        except ZeroDivisionError:
            two_to_nine_reviews_avg = 0
            pass
        try:    
            ten_to_nineteen_reviews_avg = str(round((round(ten_to_nineteen_reviews / ten_to_nineteen_reviews_count, 3) * 20), 2)) + "%"
        except ZeroDivisionError:
            ten_to_nineteen_reviews_avg = 0
            pass
        try:    
            twenty_plus_reviews_avg = str(round((round(twenty_plus_reviews / twenty_plus_reviews_count, 3) * 20), 2)) + "%"
        except ZeroDivisionError:
            twenty_plus_reviews_avg = 0
            pass
        
        print(f'{one_review_count} audience reviewers with one review gave an average rating of {one_review_avg}.')
        print(f'{two_to_nine_reviews_count} audience reviewers with 2-9 reviews gave an average rating of {two_to_nine_reviews_avg}.')
        print(f'{ten_to_nineteen_reviews_count} audience reviewers with 10-19 reviews gave an average rating of {ten_to_nineteen_reviews_avg}.')
        print(f'{twenty_plus_reviews_count} audience reviewers with 20+ reviews gave an average rating of {twenty_plus_reviews_avg}.')

tomato_peeler = TomatoPeeler()

result = tomato_peeler.generate_input_url()
print(result)

audience_reviews_url = tomato_peeler.generate_audience_reviews_input_url()
#print(audience_reviews_url)

response_text = tomato_peeler.get_url()
#print(response_text)

audience_reviews_response_text = tomato_peeler.get_audience_reviews_url()
#print(audience_reviews_response_text)

published_scores_result = tomato_peeler.parse_and_print_score_elements()
#print(element_ids)

audience_reviews = tomato_peeler.parse_audience_review_table()
#print(audience_reviews)

audience_reviews_with_count = tomato_peeler.gather_audience_review_count()
#print(audience_reviews_with_count)

results = tomato_peeler.calc_review_ranges_from_audience_reviews_dict()
pprint.pprint(f'published_scores: {published_scores_result}')