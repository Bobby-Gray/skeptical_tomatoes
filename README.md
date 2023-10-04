# skeptical_tomatoes

**Overview:**
A python script to parse all audience review profiles and their individual scores for a specified movie or series on Rotten Tomatoes, categorize audience scores by the number of reviews they have submitted, and calculate the scores for each category. 

**Why?:**
I loved Rotten Tomatoes a decade ago due to the fact that thier scores were more objectively accurate compared to other movie/tv review sites. Over the past few years, there have been many cases where a movie or tv show seemed to have a significantly higher critics score than would be expected. The reasons behind this are fairly obvious and a separate issue that has been thoroughly discussed. 

This has led myself and many others to more frequently rely upon the audience score as a higher quality metric. However, the trustworthyness of this metric has also seemed to decline significantly as of late. While looking at some of the audience reviews for the Star Wars: Ahsoka series recently, I came across many positive audience reviews that seemed suspicious due to being either broadly positive/generic or simply very short. Clicking the profile for the audience reviewer, I found that many had only a single review for Ahsoka.

Out of curiousity, I began writing this script to automate the task of collecting each audience reviewers review count so that I can sort and filter scores based on the number of reviews individual profiles have without using the official API.  

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