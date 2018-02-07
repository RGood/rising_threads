import time

class ScoreFilter:
	def __init__(self, max_size):
		self.max_size = max_size
		self.elements = []

	def insert(self, name, score):
		index = 0
		while(index < len(self.elements) and self.elements[index]['score'] < score):
			index+=1
		self.elements.insert(index,{
			'score': score,
			'name': name,
			'time': time.time()
		})
		while(len(self.elements) > self.max_size):
			self.remove_oldest()

		return index / len(self.elements)

	def remove_oldest(self):
		index = 0
		min_index = 0
		insert_time = time.time()
		for e in self.elements:
			if e['time'] < insert_time:
				insert_time = e['time']
				min_index = index
			index+=1
		return self.elements.pop(min_index)

	def is_full(self):
		return (self.max_size / 5) < len(self.elements)