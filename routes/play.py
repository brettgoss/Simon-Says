# stdlib
import json
from random import randint

# 3rd party
from flask import \
    Blueprint,\
    current_app, \
    request,\
    redirect, \
    render_template, \
    url_for

 # local
from database import Database

db = Database()

routes = Blueprint('play_routes', __name__, template_folder='templates')


@routes.route("/play")
def simon_says():
	user_id = request.cookies.get('simon-says-by-zen')

	# Check if the user has credentials
	if not user_id:
		return redirect(url_for('index_routes.login'))

	# Check if the cookie is valid
	user = db.get_username(user_id)
	if not user:
		return redirect(url_for('index_routes.login'))

	return render_template('simon_says.html', user=db.get_username(user_id), high_score=db.get_high_score(user_id))

@routes.route("/get-move", methods=['POST', 'GET'])
def get_move():
	user_id = request.cookies.get('simon-says-by-zen')
	data = json.loads(request.data)
	moves = data.get('moves')
	new_game = data.get('new')

	# Check if the user has started a new game
	if new_game:
		db.set_score(user_id, 0)
		db.reset_moves(user_id)

	# Get the users score, get a new move
	users_score = db.get_score(user_id)
	moves = db.add_move(user_id)
	return json.dumps({'moves': moves, 'user': users_score})

@routes.route("/check-move", methods=['POST'])
def check_move():
	user_id = request.cookies.get('simon-says-by-zen')
	data = json.loads(request.data)
	simons_moves = data.get('simons_moves')
	users_moves = data.get('moves')
	timeout = data.get('timeout')
	
	len_users_moves = len(users_moves)
	len_simons_moves = len(simons_moves)

	users_score = db.get_score(user_id)

	def lose():
		db.reset_moves(user_id)
		new_hs = db.update_high_score(user_id)
		if new_hs is None:
			return {'valid': False, 'user': users_score}
		return {'valid': False, 'user': users_score, 'high_score': new_hs}
		
	# Check if the user has made a move
	if len_users_moves == 0:
		return json.dumps(lose())

	# Check if the user has run out of time
	if timeout and len_users_moves < len_simons_moves:
		return json.dumps(lose())

	# A user should never have more moves than simon, but JIC
	if len_users_moves > len_simons_moves:
		return json.dumps(lose())

	# Cast simons moves to the length of user moves and compare
	simons_moves = simons_moves[:len_users_moves]
	if simons_moves == users_moves:
		if len_simons_moves == len_users_moves:
			users_score = db.increment_score(user_id)
		return json.dumps({'valid': True, 'user': users_score})
	
	return json.dumps(lose())
