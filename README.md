# skeptical_tomatoes

**Overview:**
A python script to parse all audience review profiles and their individual scores for a specified movie or series on Rotten Tomatoes, categorize audience scores by the number of reviews they have submitted, and calculate the scores for each category. 

**Why?:**
I loved Rotten Tomatoes a decade ago due to the fact that thier scores were more objectively accurate compared to other movie/tv review sites. Over the past few years, there have been many cases where a movie or tv show seemed to have a significantly higher critics score than would be expected. The reasons behind this are fairly obvious and a separate issue that has been thoroughly discussed. 

This has led myself and many others to more frequently rely upon the audience score as a higher quality metric. However, the trustworthyness of this metric has also seemed to decline significantly as of late. While looking at some of the audience reviews for the Star Wars: Ahsoka series recently, I came across many positive audience reviews that seemed suspicious due to being either broadly positive/generic or simply very short. Clicking the profile for the audience reviewer, I found that many had only a single review for Ahsoka.

Out of curiousity, I began writing this script to automate the task of collecting each audience reviewers review count so that I can sort and filter scores based on the number of reviews individual profiles have without using the official API.  

One important thing to note in regards to the % score rotten tomatoes provides is that the score is not necessarily reflective of the score or average score given by the audience or critic but the percentage of critics/audience reviewers that rated it 60% or higher (or >3.5/5). For example, an audience score of 70% means that 70% of audience members rated this title 60% or higher. This means that if 100% of critics/audience reviewers gave the title a rating of 61%, the title will be scored at 100%. 

**WARNING:** Running this may get your access to Rotten Tomatoes rate limited or blocked. I highly recommend running this script from a vpn. 

**Example Output for Ahsoka:**
760 audience reviewers with one review gave an average rating of 71.22%.
702 audience reviewers with 2-9 reviews gave an average rating of 62.26%.
246 audience reviewers with 10-19 reviews gave an average rating of 51.92%.
29 audience reviewers with 20+ reviews gave an average rating of 62.42%.
published_scores: {
  'audience_score:': 71, 'audience_review_count:': 1991, "
 'audience_average_rating:': '3.8', 
 'audience_disliked_count:': 1475, 
 'audience_liked_count:': 3569, 
 'audience_rating_total:': 5044, 
 'critics_score:': 86, 
 'critics_average_rating:': '7.35', 
 'critics_disliked_count:': 32, 
 'critics_liked_count': 224}