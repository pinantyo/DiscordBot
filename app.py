from flask import Flask, request, jsonify

import models

app = Flask(__name__)




answers = [
  "Silahkan daftar kelas TORCHE di https://torche.app/registration",
  "Bisa daftar kelas di https://torche.app/registration",
  "Kalau mau daftar les/kursus, bisa di https://torche.app/registration",
  "Semua kelas yang tersedia di TORCHE bisa dilihat di https://torche.app/courses"
]



@app.route('/', methods=['GET'])
def init():
	model = models.SentenceSimilarity()
	return 'Model Active.'



@app.route('/chatbot', methods=['POST'])
def interact_with_chatbot():
	question = request.json['question']

	try:
		answer = model.similarity_sentences(question, answers)
	except:
		results = 'Jawaban tidak dapat ditemukan.'
		status_code = '500'
	else:
		results = answer
		status_code = 200

	content = {
		'status':status_code,
		'res':results
	}

	return jsonify(content)