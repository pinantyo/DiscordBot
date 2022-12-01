import os
import discord
import requests


TOKEN = "MTA0MzEyMTAzOTc0NTQ5OTEzNg.GaKyeV.cp1PrjJFKHd3j7X8U4Qn3n1-Fw_V_V90X0DSos"
URL = 'http://127.0.0.1:5000'


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
	if message.author == client.user:
		return

	# Penambahan trigger dapat dihilangkan (Berdampak pada penggunaan hardware)
	# if message.content.startswith('!'):
	cleaned_message = {
		'question': message.content #"".join(message.content.split("!")[1])
	}

	result = requests.post(URL, json=cleaned_message)
	await message.channel.send(result.json()['res'])


client.run(TOKEN)