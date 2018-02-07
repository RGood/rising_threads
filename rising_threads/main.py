# oauth PRAW template by /u/The1RGood #
#==================================================Config stuff====================================================
import time, praw
import webbrowser
from flask import Flask, request
from threading import Thread
import configparser
from lib.new_reader import *
from lib.frontpage_scanner import *
from lib.predictor import *
import pymongo

config = configparser.ConfigParser()
config.read('../rt_info.cfg')

db_client = pymongo.MongoClient(config.get('Mongo Data','mongo_address'), config.get('Mongo Data','mongo_port'))
db = db_client['rising_threads']
coll = db['posts']

#==================================================End Config======================================================
#==================================================OAUTH APPROVAL==================================================
app = Flask(__name__)

CLIENT_ID = config.get('Reddit Access','cid')
CLIENT_SECRET = config.get('Reddit Access','csec')
REDIRECT_URI = config.get('Reddit Access','callback')
scope = config.get('Reddit Access','scope')

#Kill function, to stop server once auth is granted
def kill():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()
	return "Shutting down..."

#Callback function to receive auth code
@app.route('/authorize_callback')
def authorized():
	r.auth.authorize(request.args.get('code', ''))
	text = 'Bot successfully started on account /u/'+r.user.me().name
	kill()
	return text
	
r = praw.Reddit(
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET,
	redirect_uri=REDIRECT_URI,
	user_agent='OAuth FLASK Template Script',
    api_request_delay=1.0)
print(r.auth.url(scope.split(' '),True))
app.run(debug=False, port=65010)
#==================================================END OAUTH APPROVAL-=============================================

predictor = Predictor(coll)
#predictor = None
new_scanner = Thread(target=NewReader(r,coll, predictor).stream_all_posts, daemon=True, args=())
new_scanner.start()
FrontpageScanner(r,coll).scan_frontpage()