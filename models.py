import tensorflow as tf

from transformers import TFAutoModel, AutoTokenizer
from sklearn.metrics.pairwise import cosine_similarity

import re


class DataProcessing():
	def __call__(self, text):
		text = text.strip().lower()
		text = re.sub(r'https?://\S+|www\.\S+', '', text)
        text = re.sub(r'[-+]?[0-9]+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        return text


class SentenceSimilarity():
	def __init__(self, model_name="indolem/indobert-base-uncased"):
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
				max_length=128,
				padding='max_length',
				truncation=True,
				output_tensors='tf'
			)

			encoding['input_ids'].append(token['input_ids'][0])
			encoding['attention_mask'].append(token['attention_mask'][0])

		encoding['input_ids'] = tf.stack(encoding['input_ids'])
		encoding['attention_mask'] = tf.stack(encoding['attention_mask'])

		return encoding


	def get_features(self, texts):
		# Text Normalization
		texts = [DataProcessing(text) for text in texts]

		# Encode Tokenized
		encoding = self.tokenize_encoding(texts)

		outputs = self._model(encoding).last_hidden_state


		att_mask = texts['attention_mask']
		mask = tf.cast(tf.broadcast_to(tf.expand_dims(att_mask, axis=-1), outputs.shape), dtype='float')

		average_pooling = tf.reduce_sum(outputs, axis=1) / tf.clip_by_value(
			tf.reduce_sum(mask, axis=1), 
			clip_value_min=1e-9, 
			clip_value_max=1
		)

		return tf.stop_gradient(average_pooling).numpy()


	def similarity_sentences(self, question, answers):
		features_q = self.get_features([question])
		features_a = self.get_features(answers)


		predictions = list(cosine_similarity(features_q, features_a))

		return answers[predictions.index(max(predictions))]



