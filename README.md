# Rising Threads 2.0

This is the spiritual successor to the original rising threads bot, developed for reddit.com

## Description

The basic concept of this bot is to look at a new post and determine whether or not it is likely to become popular. The process for doing this is as follows:

1. Catalog parameters of new posts as they're submitted. Asign new posts a default position of 1000.
2. Scan the top 1000 posts on reddit for submissions that were cataloged this way and update their score position.
3. Use cataloged posts that are at least 10 hours old (to ensure they either did or did not make it to the front page at that time) as the training data for a linear regression model. The input being post parameters, the output being the post's top position.
4. Use the linear regression model to generate predictive scores for new posts.
5. Log the posts with their predicted score in a data-structure that stores 10000 elements, which are curated as first-in-first-out, while sorted by their predicted score.
6. Examine the ratio of posts that achieved a position higher than 100 to all posts cataloged.
7. If a post inserted in the data-structure ends up in a position better than this ratio, flag it as a probable popular post.
8. Post the flagged submission to reddit.

## Prerequisites

- Flask
- Pymongo
- Sklearn
- PRAW
- A MongoDB instance

## More Info

License: MIT

Author: The1RGood / Randy Goodman

Contact: randy@kindofabigdeal.org