import time
import sys, traceback
from threading import Thread
from expiringdict import ExpiringDict

class NewReader:
	def __init__(self, reddit, db_collection, predictor):
		self.reddit = reddit
		self.collection = db_collection
		self.predictor = predictor
		self.subreddit = self.reddit.subreddit('risingthreads')
		self.user_cache = ExpiringDict(max_len=1000000, max_age_seconds=86400)

	def stream_all_posts(self):
		counter = 0
		while(True):
			try:
				for post in self.reddit.subreddit('all').stream.submissions():
					try:
						if(not self.user_cache.__contains__(post.author.name)):
							self.user_cache[post.author.name] = post.author
						entry = {
							'title_length': len(post.title),
							'time': post.created_utc,
							'sub_count': post.subreddit.subscribers,
							'active_users': post.subreddit.accounts_active,
							'name_hash': hash(post.subreddit.name),
							'subreddit': post.subreddit.display_name,
							'author_link': self.user_cache[post.author.name].link_karma,
							'author_comment': self.user_cache[post.author.name].comment_karma,
							'age': time.time() - post.created_utc,
							'post_karma': post.ups,
							'num_comments': post.num_comments,
							'num_crossposts': post.num_crossposts,
							'post_type': self.get_post_type(post),
							'top_position': 1000,
							'gilded': post.gilded,
							'id': post.id
						}
						res = self.collection.insert_one(entry)
						counter+=1
						if(self.predictor!=None):
							if(counter%100==0):
								self.predictor.async_reset()
							if(self.predictor.predict(post.id)):
								print("Submitting post")
								title = "r/{0}: {1} by /u/{2} ({3} mins. old)".format(post.subreddit.display_name, post.title, post.author.name, str(int((time.time() - post.created_utc) / 60)))
								self.subreddit.submit(title, url = 'https://www.reddit.com'+post.permalink)
					except:
						traceback.print_exc(file=sys.stdout)
			except KeyboardInterrupt:
				print("Stopping.")
				break
			except:
				traceback.print_exc(file=sys.stdout)

	def get_post_type(self, post):
		if(post.is_self):
			return 0
		elif(post.is_video):
			return 2
		else:
			return 1