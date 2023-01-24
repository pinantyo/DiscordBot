import tensorflow as tf

from transformers import TFAutoModel, AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

import re


class DataProcessing():
	def __init__(self, data):
		self.data = data


	def normalize_text(self):
		text = self.data.lower()
		text = re.sub(r'https?://\S+|www\.\S+', '', text)
		text = re.sub(r'[-+]?[0-9]+', '', text)
		text = re.sub(r'[^\w\s]', '', text)
		text = text.strip()
		return text


class SentenceSimilarity():
	def __init__(self, model_name="cahya/bert-base-indonesian-1.5G"):
		self._model = TFAutoModel.from_pretrained(
			model_name, 
			from_pt=True, 
			output_hidden_states=True, 
			trainable=False
		)

		self._tokenizer = AutoTokenizer.from_pretrained(model_name)


	def tokenize_encoding(self, text):

		encoding = {'input_ids':[], 'attention_mask':[]}

		for i in text:
			token = self._tokenizer.encode_plus(
				i,
				max_length=64,
				padding='max_length',
				truncation=True,
				return_tensors='tf'
			)

			encoding['input_ids'].append(token['input_ids'][0])
			encoding['attention_mask'].append(token['attention_mask'][0])

		encoding['input_ids'] = tf.stack(encoding['input_ids'])
		encoding['attention_mask'] = tf.stack(encoding['attention_mask'])

		return encoding


	def get_features(self, texts):
		# Text Normalization
		texts = [DataProcessing(text).normalize_text() for text in texts]

		# Encoding
		encoding = self.tokenize_encoding(texts)

		# Get last fully connected layers
		outputs = self._model(encoding).last_hidden_state


		att_mask = encoding['attention_mask']
		mask = tf.cast(tf.broadcast_to(tf.expand_dims(att_mask, axis=-1), outputs.shape), dtype='float')

		average_pooling = tf.reduce_sum(outputs, axis=1) / tf.clip_by_value(
			tf.reduce_sum(mask, axis=1), 
			clip_value_min=1e-9, 
			clip_value_max=1
		)

		return tf.stop_gradient(average_pooling).numpy()



	def max_axis(self, list_val, axis):
		"""
			Get highest probabilities index
		"""
		current = list_val[0]

		for i in list_val:
			if i[axis] > current[axis]:
				current = i

		return current[0]


	def similarity_sentences(self, question, answers):
		features_q = self.get_features([question])
		features_a = self.get_features(answers)


		predictions = list(cosine_similarity(features_q, features_a).reshape(-1))

		"""
			Limitasi threshold
		"""
		predictions = [(i, prediction) for i, prediction in enumerate(predictions) if prediction > 0.6]

		if len(predictions) == 0:
			predictions = "Jawaban tidak dapat ditemukan"
			return predictions

		return answers[self.max_axis(predictions, axis=1)]



class QuestionAnsweringSystem():
	def __init__(self, model_name="indobenchmark/indobert-base-p2"):
		self.__tokenizer = BertTokenizer.from_pretrained(model_name)
		self.__model = BertForQuestionAnswering.from_pretrained(model_name)


	def ask(question, context):
	  	# Init
	  	answer = ""

	  	# Normalisasi
	  	question_normalized = DataProcessing(question).normalize_text()

	  	# Tokenisasi - Convert string
	  	input_ids = tokenizer.encode(
	      	question_normalized, 
	      	context,
	  	)

	  	tokens_ids_converted = tokenizer.convert_ids_to_tokens(input_ids)

	  	# Ambil seperator untuk memisahkan question dan context
	  	separator_ids = input_ids.index(tokenizer.sep_token_id)

	  	segment_text_q = separator_ids + 1
	  	segment_text_a = len(input_ids) - segment_text_q

	  	segmented_text_ids = [0]*segment_text_q + [1]*segment_text_a

	  	# Pengecekan segmentasi question dan context menghasilkan panjang tokenisasi yang sama
	  	assert len(segmented_text_ids) == len(input_ids)

	  	# Prediksi
	  	outputs = model(
	      	torch.tensor([input_ids]), 
	      	token_type_ids = torch.tensor([segmented_text_ids])
	  	)

	  	answer_start = torch.argmax(outputs.start_logits)
	  	answer_end = torch.argmax(outputs.end_logits)

	  	if answer_end >= answer_start:
	    	answer = tokens_ids_converted[answer_start]

	    	for i in range(answer_start+1, answer_end+1):
	      		if tokens_ids_converted[i][0:2] == "##":
	        		answer += tokens_ids_converted[i][2:]
	      		else:
	        		answer += " " + tokens_ids_converted[i]
	    
	  
	  	if answer.startswith("[CLS]"):
	    	answer = "Jawaban tidak ditemukan"
	  
	  	return answer.capitalize()



