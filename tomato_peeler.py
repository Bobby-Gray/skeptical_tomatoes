from bs4 import BeautifulSoup
import requests
import json 

class TomatoPeeler:
    def __init__(self):
        self.tv_or_movie = input("Enter tv or movie: ")
        if self.tv_or_movie == "tv":
            self.property = input("Enter movie or tv series name as it appears in the RT url. e.g., 'star_wars_ahsoka': ")
            self.season = input("Enter season of tv series as 's' + season number. e.g., 's01': ")
            self.entity_uri = "/tv/" + self.property + "/" + self.season

        elif self.tv_or_movie == "movie":
            self.property = input("Enter movie or tv series name as it appears in the RT url. e.g., 'star_wars_ahsoka': ")
            self.entity_uri = "/m/" + self.property

        else:
            print("Uh oh! Something broke.")
            exit

    def generate_input_url(self):
        self.base_url = "https://rottentomatoes.com"
        self.url = self.base_url + self.entity_uri
        return self.url
    
    def generate_audient_reviews_input_url(self):
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
    
    def parse_and_print_element_ids(self, response_text):
        soup = BeautifulSoup(response_text, 'html.parser')
        element_ids = soup.find_all(id=True)
        
        if element_ids:
            print("Element IDs found in the response:")
            for element in element_ids:
                #print(element['id'])
                if "scoreDetails" in element['i`d']:
                    score_details = json.loads(element.contents[0])
                    #print(json.dumps(score_details, indent=4, sort_keys=True))
                    audience_score_all = score_details['modal']['audienceScoreAll']
                    audience_score = audience_score_all.get('value')
                    average_rating = audience_score_all.get('averageRating')
                    disliked_count = audience_score_all.get('notLikedCount')
                    liked_count = audience_score_all.get('likedCount')
                    print(f'audience score: {audience_score}')
                    print(f'average_rating: {average_rating}')
                    print(f'disliked_count: {disliked_count}')
                    print(f'liked_count: {liked_count}')
        else:
            print("No element IDs found in the response.")

tomato_peeler = TomatoPeeler()

result = tomato_peeler.generate_input_url()
print(result)

audience_reviews_url = tomato_peeler.generate_audient_reviews_input_url()
print(audience_reviews_url)

response_text = tomato_peeler.get_url()
#print(response_text)

# Call the parse_and_print_element_ids method to parse and print element IDs
element_ids = tomato_peeler.parse_and_print_element_ids(response_text)
print(element_ids)
