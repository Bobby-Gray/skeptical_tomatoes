# skeptical_tomatoes

**Overview:**
A python script to parse all audience reviewer ids and their individual scores for a specified movie or series on Rotten Tomatoes, categorize audience reviewer and score by the number of reviews they have submitted, and calculate the scores for each category. 

**WARNING:** Running this may get your access to Rotten Tomatoes rate limited or blocked. I highly recommend running this script from a vpn. 

Example Output:
  
  **Published Scores:** published_scores: {
    'audience_score:': 73, 
    'audience_average_rating:': '3.9', 
    'audience_disliked_count:': 1191, 
    'audience_liked_count:': 3236, 
    'audience_total:': 4427, 
    'critics_score:': 88, 
    'critics_average_rating:': '7.40', 
    'critics_disliked_count:': 26, 
    'critics_liked_count': 205
    }
  
  **Audience Score by Review Count:**
  * 2214 audience reviewers with one review gave an average rating of 67.84%.
  * 1476 audience reviewers with 2-9 reviews gave an average rating of 35.23%.
  * 737 audience reviewers with 10+ reviews gave an average rating of 30.53%.