from app import app
from threading import Thread
import os

def run():
  app.run(host='0.0.0.0',port=os.environ.get('PORT', 5000))

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
	# keep_alive()
  run()
	