from bs4 import BeautifulSoup
import requests
import json 

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

    def parse_and_print_audience_reviews_element_ids(self, audience_reviews_response_text):
        soup = BeautifulSoup(audience_reviews_response_text, 'html.parser')
        element_ids = soup.find_all(id=True)
        audience_count = self.audience_total
        if element_ids:
            print("Element IDs found in the response:")
            for element in element_ids:
                print(element['id'])
                profiles = {}
                index = 0
                #while index < 40:
                if "reviews" in element['id']:
                    #print(element)
                    reviews = soup.find_all("div", {"class": "audience-review-row"})
                    prevnext = soup.find("div", {"class": "prev-next-paging__wrapper"})
                    prevnext1 = prevnext.find("rt-button", {"class": "next hide"})
                    prevnext2 = prevnext1.click("Next")
                    print(f'PAGING: {prevnext}')
                    print(f'prevnext1: {prevnext1}')
                    print(f'prevnext2: {prevnext2}')
                    #prevnext1.click()
                    for review in reviews:
                        score = 0
                        #print(f'each: {review}')
                        base_url = "https://rottentomatoes.com"
                        profile = review.a['href']
                        score_meta = review.find("span", {"class": 'star-display'})
                        for score_stars in score_meta:
                            #print(f'score_stars: {score_stars}')
                            if "filled" in str(score_stars):
                                score += 1
                            elif "star-display__half" in str(score_stars):
                                score += .5
                            else:
                                pass
                        #print(f'score_meta: {score_meta}')
                        
                        profiles.update({base_url + profile: score})
                        #profiles.append(score)
                        #print(f'score: {score}')
                        #print(f'profile: {profile}')
                        index += 1
                        #print(f'profile: {profile}') 
                    return profiles, index, prevnext                        


                            # profile_id = str(review['a href'])
                            # print(f'profile_id: {profile_id}')

                        
                            # try:
                            #     # Go to page 2
                            #     next_link = browser.find_element_by_xpath('//*[@title="Go to page 2"]')
                            #     next_link.click()
                            #     index = 0

                            #     # update html and soup
                            #     html = browser.page_source
                            #     soup = BeautifulSoup(html, "html.parser")

                            #     time.sleep(30)
                            # except NoSuchElementException:
                            #     rows_remaining = False
        else:
            print("No element IDs found in the response.")
        print(profiles)
        print(index)


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
audience_reviews_element_ids = tomato_peeler.parse_and_print_audience_reviews_element_ids(audience_reviews_response_text)
print(audience_reviews_element_ids)
