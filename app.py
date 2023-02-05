from flask import Flask, request, jsonify

import models

app = Flask(__name__)




answers = [
  "Silahkan daftar kelas TORCHE di https://torche.app/registration",
  "Bisa daftar kelas di https://torche.app/registration",
  "Kalau mau daftar les/kursus, bisa di https://torche.app/registration",
  "Semua kelas yang tersedia di TORCHE bisa dilihat di https://torche.app/courses"
]

context = """Torche Education adalah Start-Up Teknologi Pendidikan pertama yang membantu anda belajar dalam bidang teknik khususnya di bidang Teknik Kimia. 
Torche memiliki lebih dari 30 mata pelajaran teknik kimia, dengan 800 siswa unik yang tersebar di lebih dari 8 universitas. 
Kami berkomitmen untuk menyediakan pendidikan tinggi yang cepat, komprehensif, dan berstandar internasional di bidang teknik kimia, 
teknik bioproses, dan pada akhirnya semua siswa engineering di seluruh dunia. Torche memiliki pengajar yang ahli di bidang teknik kimia 
dan telah berpengalaman bekerja di perusahaan nasional maupun multinasional, baik di Indonesia maupun di luar negeri. """

mode = 'similarity'

@app.route('/', methods=['GET','POST'])
def init():
	global model, model_qas, mode
	
	if request.method == 'GET':
		model = models.SentenceSimilarity()
		model_qas = models.QuestionAnsweringSystem()
		return 'Model Active.'

	elif request.method == 'POST':
		question = request.json['question']
		mode = request.json['mode'] if request.json['mode'] else mode

		if request.json['mode']:
			status_code = 200
			results = f'mode {mode} switched'

		else:
			try:
				if mode == 'similarity':
					answer = model.similarity_sentences(question, answers)
				else:
					answer = model_qas.ask(question, context)

			except:
				results = 'Mesin tidak aktif.'
				status_code = '500'
			else:
				results = answer
				status_code = 200

		content = {
			'status':status_code,
			'res':results
		}

		return jsonify(content)
	

		