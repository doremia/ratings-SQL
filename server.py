"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("users.html",users=users)

@app.route('/register', methods=["GET"])
def register():
    """Register a user"""
    return render_template("register.html")


@app.route('/register', methods=["POST"])
def store_user():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter(User.email==email).first()

    if not user:
        new_user = User(email=email,
                        password=password)
        db.session.add(new_user)
        db.session.commit()

    return redirect('/')


@app.route('/login')
def log_in():
    return render_template('login.html')


@app.route('/logged-in')
def logged_in():
    #complains if nothing in form
    email = request.args.get('email')
    password = request.args.get('password')

    user = User.query.filter(User.email==email).first()

    if user:
        if user.password == password:
            flash('Logged in')
            session['user'] = email
            return redirect('/')
        else:
            flash('Wrong Password')
            return redirect('/login')
    else:
        flash('No User With that Email')
    return redirect('/login')


@app.route('/logout')
def logout():
    if session.get('user'):
        session['user'] = None
        flash('Logged out')
    else:
        flash('You are not logged in')
    return redirect('/')

@app.route('/users/<user_id>')
def show_use_info(user_id):

    user = User.query.filter(User.user_id==user_id).one()

    ratings_list = user.ratings #a list of ratings objects

    # movie_list = []
    # for rating in ratings_list:
    #     movie_list.append(rating.movie) #list of movie objects


    return render_template('show_info.html',
                            user=user,
                            ratings=ratings_list)

@app.route('/movies')
def show_movie_list():
    
    movies = Movie.query.all() #list of movie objects

    return render_template('movie_list.html', movies = movies)

@app.route('/movies/<movie_id>')
def show_movie_info(movie_id):

    movie = Movie.query.filter(Movie.movie_id == movie_id).one()

    return render_template('show_movie_info.html', 
                            movie = movie,
                          )

@app.route('/set-rating', methods=['GET'])
def confirm_set_rating():
    movie_id = request.args.get('movie_id')
    if session.get('user'):
        movie = Movie.query.filter(Movie.movie_id == movie_id).one()
        return render_template('set_rating.html', movie=movie)
    flash('You are not logged in!')
    return redirect(f'/movies/{movie_id}')


@app.route('/set-rating', methods=['POST'])
def set_rating():
    movie_id = request.form.get('movie_id')
    score = int(request.form.get('score'))

    email = session['user']
    user = User.query.filter( User.email == email ).one()

    #to be done: handle both the case where this is a new rating and 
    #the case where this is updating an existing rating

    return redirect(f'/movies/{movie_id}')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
