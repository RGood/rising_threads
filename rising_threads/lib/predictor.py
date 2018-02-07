from sklearn.linear_model import LinearRegression
from .score_filter import ScoreFilter
import time
from threading import Thread
from collections import defaultdict

class Predictor:
	def __init__(self, db_collection):
		self.collection = db_collection
		self.score_filter = ScoreFilter(10000)
		self.sub_weight = defaultdict(lambda: [0,1])
		self.reset()

	def gen_new_clf(self):
		new_clf = LinearRegression()
		data = self.collection.find({'time' : {'$lt': time.time() - (60 * 60 * 10)}})
		seed_data = []
		seed_results = []

		for entry in data:
			valid = True
			for v in entry.values():
				if v.__class__.__name__ == 'dict':
					self.collection.remove({'id': entry['id']})
					valid = False
					break
			if(valid):
				top_pos = [entry['top_position']]
				entry_id = entry['id']
				entry['weight'] = self.sub_weight[entry['subreddit']][0] / self.sub_weight[entry['subreddit']][1]
				entry.__delitem__('top_position')
				entry.__delitem__('_id')
				entry.__delitem__('id')
				entry.__delitem__('subreddit')
				entry.__delitem__('name_hash')
				for v in entry.values():
					if(v.__class__.__name__ != 'int' and v.__class__.__name__ != 'long' and v.__class__.__name__ != 'float'):
						print('removing entry')
						print(entry.values())
						print(entry_id)
						self.collection.remove({'id': entry_id})
						valid = False
						break
			if(valid):
				seed_results += [top_pos]
				seed_data += [self.get_ordered_values(entry)]
			

		new_clf.fit(seed_data, seed_results)
		return new_clf

	def training_filter(self, entry):
		return True

	def reset_sub_weight(self):
		new_weight = defaultdict(lambda: [0,1])
		
		data = self.collection.find({'time' : {'$lt': time.time() - (60 * 60 * 10)}})
		for entry in data:
			valid = True
			for v in entry.values():
				if v.__class__.__name__ == 'dict':
					self.collection.remove({'id': entry['id']})
					valid = False
					break
			if(valid):
				if(entry['top_position'] < 100):
					new_weight[entry['subreddit']][0]+=1
				new_weight[entry['subreddit']][1]+=1
		self.sub_weight = new_weight

	def reset(self):
		print("Resetting Predictor")
		self.reset_sub_weight()
		self.clf = self.gen_new_clf()
		print("Reset Complete")

	def async_reset(self):
		reset_thread = Thread(target=self.reset, args=())
		reset_thread.start()

	def predict(self, entry_id):
		entry = self.collection.find_one({'id': entry_id})
		if(entry == None):
			raise NameError('Entry with that ID could not be found.')
		y_value = [entry['top_position']]
		name = entry['id']
		entry['weight'] = self.sub_weight[entry['subreddit']][0] / self.sub_weight[entry['subreddit']][1]
		values = list(entry.values())

		weight_str = "{0} / {1}".format(self.sub_weight[entry['subreddit']][0], self.sub_weight[entry['subreddit']][1])
		entry.__delitem__('top_position')
		entry.__delitem__('_id')
		entry.__delitem__('id')
		entry.__delitem__('subreddit')
		entry.__delitem__('name_hash')
		prediction = self.clf.predict([self.get_ordered_values(entry)])[0]
		weight = self.score_filter.insert(name, prediction)
		if(weight == 0):
			print('============NEW LEADER============')
			print(values)
			print("{0}, {1}".format(prediction, weight))
			print(weight_str)
			print('==================================')
		elif(weight < 0.001):
			print('=========NEW Probably FP==========')
			print(values)
			print("{0}, {1}".format(prediction, weight))
			print(weight_str)
			print('==================================')
		elif(weight < 0.50):
			print(values)
			print("{0}, {1}".format(prediction, weight))
			print(weight_str)
		return self.score_filter.is_full() and (weight < (self.collection.find({ 'top_position': { '$lt': 101 }}).count() / self.collection.find().count()))

	def get_ordered_values(self, entry):
		keys = list(entry.keys())
		keys.sort()
		values = []
		for k in keys:
			values+=[entry[k]]
		return values