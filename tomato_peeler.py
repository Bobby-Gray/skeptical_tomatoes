from bs4 import BeautifulSoup
import json 
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
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
    
    def parse_and_print_element_ids(self):
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
                    self.audience_total = int(audience_liked_count + audience_disliked_count)
                    critics_average_rating = critics_score_all.get('averageRating')
                    critics_disliked_count = critics_score_all.get('notLikedCount')
                    critics_liked_count = critics_score_all.get('likedCount')
                    critics_score = critics_score_all.get('value')
                    self.published_scores = {'audience_score:': audience_score, 
                                        'audience_average_rating:': audience_average_rating,
                                        'audience_disliked_count:': audience_disliked_count,
                                        'audience_liked_count:': audience_liked_count,
                                        'audience_total:': self.audience_total,
                                        'critics_score:': critics_score,
                                        'critics_average_rating:': critics_average_rating,
                                        'critics_disliked_count:': critics_disliked_count,
                                        'critics_liked_count': critics_liked_count}
                    print(f'published_scores: {self.published_scores}')
                    return self.published_scores
        else:
            print("No element IDs found in the response.")

    def parse_and_print_audience_reviews_element_ids(self):
        link = self.generate_audience_reviews_input_url()
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        with webdriver.Chrome(options=op) as driver:
            driver.get(link)
            time.sleep(1)
            review_table_len = len(driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div'))
            self.reviews = {}
            index = 1
            outer_tries = 5
            while outer_tries:
                try:
                    index_review_len = int(review_table_len)
                    # next_page = driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]')
                    inner_tries = 5
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
                            inner_tries -= 1
                            if inner_tries:
                                continue
                            else: 
                                break
                    driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]').click()
                    time.sleep(2)
                    index_review_len = len(driver.find_elements(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div'))
                    next_page_button = str(driver.find_element(By.XPATH,'//*[@id="reviews"]/div[3]/rt-button[2]').get_attribute("innerHTML"))
                    next_review_row_profile = driver.find_element(By.XPATH, '//*[@id="reviews"]/div[2]/div[2]/div[' + str(index_review_len) + ']/div[1]/div/a').get_attribute("href")
                    reviews_len = len(self.reviews)
                    print(f'next review row profile: {next_review_row_profile} table_len: {reviews_len}')
                    inner_outer_tries = 3
                    if next_review_row_profile in self.reviews.keys():
                        inner_outer_tries -= 1
                        if "next hide" in next_page_button:
                            print(f'Next page button hidden: {next_page_button}')
                            inner_outer_tries = 0
                            inner_tries = 0
                            outer_tries = 0
                            driver.quit()
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
        for reviewer, score in self.audience_reviews_dict.items():
            tries = 3
            print(f'Gathering audience review count from profile: {reviewer}')
            reviewer_s = str(reviewer)
            review_count = 0 
            op = webdriver.ChromeOptions()
            op.add_argument('headless')
            with webdriver.Chrome(options=op) as driver:
                try:
                    link_replace = reviewer_s.replace("/profiles/","/profiles/ratings/")
                    tv_link = link_replace + "/tv"
                    movie_link = link_replace + "/movie"
                    driver.get(tv_link)
                    time.sleep(1)
                    tv_review_table = driver.find_element(By.XPATH, '//*[@id="profiles"]/div/div[3]').get_attribute("innerHTML")
                    if tv_review_table is not None:
                        tv_review_s = str(tv_review_table)
                        tv_review_count = tv_review_s.count('profile-rating reviewpresent')
                        review_count += tv_review_count
                    driver.get(movie_link)
                    time.sleep(1)
                    movie_review_table = driver.find_element(By.XPATH, '//*[@id="profiles"]/div/div[3]').get_attribute("innerHTML")
                    if movie_review_table is not None:
                        movie_review_s = str(movie_review_table)
                        movie_review_count = movie_review_s.count('profile-rating reviewpresent')
                        review_count += movie_review_count
                except Exception as err:
                        print(err)
                        if tries:
                            tries -= 1
                            continue
                        else:
                            driver.close()
                            break
                self.audience_reviews_dict.update({ reviewer : [score[0], review_count]})
                driver.close()        
        driver.quit()
        return self.audience_reviews_dict
    
    def calc_review_ranges_from_audience_reviews_dict(self):
        self.audience_reviews_dict_completed = self.audience_reviews_dict
        one_review = 0
        one_review_count = 0
        two_to_nine_reviews = 0
        two_to_nine_reviews_count = 0
        ten_plus_reviews = 0
        ten_plus_reviews_count = 0  
        for context in self.audience_reviews_dict_completed.values():
            if context[1] <= 1:
                one_review += context[0]
                one_review_count += 1
            elif 1 < context[1] < 10:
                two_to_nine_reviews += context[0]
                two_to_nine_reviews_count += 1
            elif context[1] >= 10:
                ten_plus_reviews += context[0]
                ten_plus_reviews_count += 1
            else:
                continue 
        one_review_avg = str(round((round(one_review / one_review_count, 3) * 20), 2)) + "%"
        two_to_nine_reviews_avg = str(round((round(two_to_nine_reviews / two_to_nine_reviews_count, 3) * 20), 2)) + "%"
        ten_plus_reviews_avg = str(round((round(ten_plus_reviews / ten_plus_reviews_count, 3) * 20), 2)) + "%"
        print(f'{one_review_count} audience reviewers with one review gave an average rating of {one_review_avg}.')
        print(f'{two_to_nine_reviews_count} audience reviewers with 2-9 reviews gave an average rating of {two_to_nine_reviews_avg}.')
        print(f'{ten_plus_reviews_count} audience reviewers with 10+ reviews gave an average rating of {ten_plus_reviews_avg}.')
    
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
published_scores_result = tomato_peeler.parse_and_print_element_ids()
#print(element_ids)

# Call the parse_and_print_element_ids method to parse and print element IDs
audience_reviews = tomato_peeler.parse_and_print_audience_reviews_element_ids()
#print(audience_reviews)

# Call the parse_and_print_element_ids method to parse and print element IDs
audience_reviews_with_count = tomato_peeler.gather_audience_review_count()
#print(audience_reviews_with_count)

# Call the parse_and_print_element_ids method to parse and print element IDs
results = tomato_peeler.calc_review_ranges_from_audience_reviews_dict()
print(f'published_scores: {published_scores_result}')