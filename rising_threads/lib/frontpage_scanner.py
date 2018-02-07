import time
class FrontpageScanner:
	def __init__(self, reddit, db_collection):
		self.reddit = reddit
		self.collection = db_collection

	def scan_frontpage(self):
		while(True):
			index = 0
			try:
				for post in self.reddit.subreddit('all').hot(limit=1000):
					entry = self.collection.find_one({'id': post.id})
					if(entry != None):
						if index < entry['top_position']:
							#print("Logged frontpage post found.")
							self.collection.update_one({'id': post.id}, {'$set': {'top_position': index}})
					index+=1
				time.sleep(30)
			except KeyboardInterrupt:
				print("Stopping.")
				break
			except:
				pass