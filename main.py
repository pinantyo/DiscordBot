import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv('DISCORD_TOKEN')
URL = os.getenv('APP_URL')
mode = 'sentence_similarity'


answers = [
	"Halo, apakah ada pertanyaan?"
	"Silahkan daftar kelas TORCHE di https://torche.app/registration",
  	"Bisa daftar kelas di https://torche.app/registration",
  	"Kalau mau daftar les/kursus, bisa di https://torche.app/registration",
  	"Semua kelas yang tersedia di TORCHE bisa dilihat di https://torche.app/courses"
]


intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
 
@client.event
async def on_ready():
	requests.get(URL)
	
	print('Bot logged in as {0.user} and model initiated'.format(client))


@client.event
async def on_message(message):
	result = 'Jawaban tidak ditemukan'
	mode = None

	if message.author == client.user:
		return

	# Penambahan trigger dapat dihilangkan (Berdampak pada penggunaan hardware)
	if message.content.startswith('/'):
		mode = "".join(message.content.split('/')[1])

	cleaned_message = {
		'question': message.content,
		'mode':mode
	}

	result = requests.post(f'{URL}', json=cleaned_message)
	await message.channel.send(result.json()['res'])
	return


client.run(TOKEN)