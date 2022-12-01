# FLASK WEB DEVELOPMENT
import flask
from flask import request, jsonify , render_template ,jsonify
from flask_cors import CORS

# requesting data and converting api info to base64
import requests
import json
import base64

# string to python class type
import ast

# check files in running machine
from os.path import exists


# debugging
import time
import pprint

# webcrawl lyrics
import bs4

# WATSON AI
import watson


# MATH
import statistics
import random



# TODO make a sql database of all the songs watson has already analyzed
# make a function to apply the database before running the analysis, check if we already have it



# # DISABLE EXTRA INFORMATION FROM LOGS
# import logging
# log = logging.getLogger('werkzeug')
# log.disabled = True




# FLASK INIT VARIABLES
application = flask.Flask(__name__ , static_url_path='', static_folder='static' , template_folder='templates')
application.config["DEBUG"] = True
application.secret_key = 'something secret'

CORS(application)





# -----------------------------------------------------------------
import config

# SPOTFIY INIT VARIABLES
spotify_clientId = config.spotify_clientId
spotify_clientSecret = config.spotify_clientSecret

# GENIUS INIT VARIABLES
genius_clientId = config.genius_clientId
genius_clientsECRET = config.genius_clientsECRET

# general use INIT VARIABLES
spotify_callbackURL = config.spotify_callbackURL
genius_callbackURL = config.genius_callbackURL


# MEME GENERATOR LOGIN
meme_username = config.meme_username
meme_password = config.meme_password
# -----------------------------------------------------------------














API_COOLDOWN_RATE = 3


# auth SPOTFITY scopes
scopes = [
 'ugc-image-upload',
 'user-read-recently-played',
 'user-top-read',
 'user-read-playback-position',
 'user-read-playback-state',
 'user-modify-playback-state',
 'user-read-currently-playing',
 'app-remote-control',
 'streaming',
 'playlist-modify-public',
 'playlist-modify-private',
 'playlist-read-private',
 'playlist-read-collaborative',
 'user-follow-modify',
 'user-follow-read',
 'user-library-modify',
 'user-library-read',
 'user-read-email',
 'user-read-private'
]
spotty_full_permission = ''
for i in scopes:
    spotty_full_permission += i + ' '


# genius scopes
genius_scopes = [
    'me',
    'create_annotation',
    'manage_annotation',
    'vote',
]
genius_full_permission = ''
for i in genius_scopes:
    genius_full_permission += i + ' '




# database check
path_to_file = "song_db.json"
if exists(path_to_file):
    pass
else:
    with open("song_db.json" , "w") as f:
        f.write("{}")





# homepage
@application.route('/', methods=['GET'])
def home():
    if "amount" not in flask.session:
       flask.session['amount'] = 0

    content = {
        'implciit_url' : authorize_spotify_IMPLICIT(),
        'refreshable_url' : authorize_spotify_REFRESHABLE()
    }
    return render_template('homepage.html' , content = content)


# spotify login
@application.route('/login/')
def logging_in():
    gen_auth_url = Oauth_function( 'https://api.genius.com/oauth/authorize' , genius_clientId , genius_callbackURL , genius_full_permission , genius_clientsECRET , 'code' )

    # refreshable
    if 'code' in flask.request.args :
        auth_code = flask.request.args['code']
        spotify_token = _retrieve_refreshable_token(auth_code)

        # ******************
        # WE ARE NOW SAVING THE TOKEN TO A WEB TECNIQUE
        # ******************

        # save to sessions
        # flask.session['spotify_token'] = spotify_token
        # return flask.redirect('/Dashboard')

        # save to url argument
        # return flask.redirect(flask.url_for('Dashboard', spotify_token = spotify_token ))

        # save to cookies 
        if 'spotify_token' in flask.session and flask.session.get('spotify_expired') == False:
            return flask.redirect( gen_auth_url )
            # return flask.redirect('/Dashboard')
        else:
            resp = flask.make_response(flask.redirect(gen_auth_url))
            # resp = flask.make_response(flask.redirect('/Dashboard'))
            flask.session['spotify_token'] = spotify_token
            flask.session['spotify_expired'] = False
            return resp
    return flask.redirect( "/" )

# genius login
@application.route('/gen_login/')
def gen_login():

    genius_token = flask.request.args.get("code")
    genius_token =  _retrieve_genius_token(genius_token)


    # save to cookies 
    if 'genius_token' in flask.session and flask.session.get('genius_expired') == False:
        return flask.redirect('/Dashboard')
    else:
        resp = flask.make_response(flask.redirect('/Dashboard'))
        flask.session['genius_token'] = genius_token
        flask.session['genius_expired'] = False
        return resp



# User Dashboard
# TODO @app.route('/user/<username>')
@application.route('/Dashboard', methods=['GET'])
def Dashboard():
    # COOKIES
    if 'spotify_token' not in flask.session or flask.session['spotify_expired'] == True:
        print(f"\n\n\n------------\nAccess denied (spotify token): {request.remote_addr}\n------------")
        return flask.redirect('/')
    elif 'genius_token' not in flask.session :
        print(f"\n\n\n------------\nAccess denied (genius token): {request.remote_addr}\n------------")
        return flask.redirect('/')

    # ************
    # RETRIEVING THE TOKEN!!!!
    # ************

    # retrieve from sessions
    # spotify_token =  flask.session['spotify_token']

    # retrieve from url arguments
    # spotify_token =  request.args.get('spotify_token')

    # retrieve from cookies
    spotify_token = flask.session.get('spotify_token')

    # fetch user data from spotify after auth functions
    user_data = fetch_spotify_data(spotify_token , 'https://api.spotify.com/v1/me' )



    # retrive amount analyzed
    if "amount" in flask.session:
        amount_analyzed = flask.session['amount']
    else:
        flask.session['amount'] = 0

    
    # USING TRY METHOD TO FIND KEYS IN user_data RESPONSE
    try:
        # save username throughout session
        flask.session['username'] = user_data['display_name']
        flask.session['email'] = user_data['email']

        # final display
        context = {
            'data' : user_data,
            'username' : flask.session['username'],
            'email' : flask.session['email'] , 
            # 'meme' : fetch_meme( text0 = f'{flask.session["username"]} thinks', text1 = "they're a data scientist..." )['data']['url'] , 
            "amount_analyzed" : amount_analyzed,
        }

        # check if meme didnt fail
        meme_pic = fetch_meme( text0 = f'{flask.session["username"]} thinks', text1 = "they're a data scientist..." )
        if "data" in meme_pic:
            context['meme'] = meme_pic['data']['url']

        return render_template('user_dashboard.html' , context = context )

    except Exception as e:
        print(e)
        print("ERROR: Dashboard()")
        flask.session['spotify_expired'] = True
        return flask.redirect( authorize_spotify_REFRESHABLE() )



# SEARCH A SONG
@application.route('/search-form', methods=['GET'])
def search_form():
    return flask.render_template('search_form.html' )
@application.route('/search-results', methods=['POST'])
def search_results():
    spotify_token = flask.session.get('spotify_token')
    q = flask.request.form.get('q')
    q_type = flask.request.form.get('q_type')

    artists = []
    tracks = []
    images = []
    # SEARCHING FOR TRACKS
    if q_type == None or q_type == 'None':
        q_type = 'track'
        # search spotify
        data = fetch_spotify_data(spotify_token, f'https://api.spotify.com/v1/search?q={q}&type={q_type}')
        q_type += 's'
        tracks = data[q_type]['items']
        

        # add images
        # for i in range(len(tracks)):
        #     tracks[i]['thumbnail'] = fetch_spotify_data(spotify_token, tracks[i]['artists'][0]['href'] )['images'][-1]['url']
        for i in tracks:
            i['thumbnail'] = fetch_spotify_data(spotify_token, i['artists'][0]['href'] )['images'][-1]['url']



    # SEARCHING FOR ARTISTS
    else:
        q_type = 'artist'
        # search spotify
        data = fetch_spotify_data(spotify_token, f'https://api.spotify.com/v1/search?q={q}&type={q_type}')
        q_type += 's'
        artists = data[q_type]['items']

    content = {
        'artists' : artists ,
        'tracks' : tracks 
    }
    return flask.render_template('search_results.html' , content = content )
@application.route('/song-analysis', methods=['POST'  ])
def song_analysis():
    spotify_token = flask.session.get('spotify_token')
    song_id = flask.request.form.get("analysis_id")
    song_title = flask.request.form.get("song_name")
    song_artist_name = flask.request.form.get("song_artist_name")
    stats = _song_analysis_details(spotify_token , song_id , False , song_title , song_artist_name)
    stats['song_title'] = song_title
    stats['song_artist_name'] = song_artist_name

    # add to total amount analyzed
    flask.session['amount'] += 1

    print("\nSEARCHED SONG "  )




    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if  stats['ai']["nlu"] is not None : 
        ai_response = True
        emotionsLabels = list(stats['ai']['nlu']['averageEmotion'].keys())
        emotionValues = [    stats['ai']['nlu']['averageEmotion'][i] for i in emotionsLabels  ]



    if ai_response: #kinda redundant but i mean.... why not have the modularity?
        content = {
            'stats'  : stats,
            'ai_response'  : ai_response,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }



    else: #NO LYRICS
        content = {
            'stats'  : stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }

    
    return flask.render_template('song_analysis.html' , content = content)




# NOTE:
    # GROUP ANALYSIS IS A LITTLE DIFFERENT FROM LIKES ANALYSIS
    # both variables are dictionaries with numbers as keys starting at zero
    # each value is another dictionary with keys :  ['owner', 'name', 'description', 'id', 'songs']
    # musicGroup['songs'] is an array with tuples 
    # each tuple is ( "id" ,  "title" , ["artists"]  )


# Album Analysis
@application.route('/album-analysis', methods=['GET'])
def album_analysis():
    # grab music
    spotify_token = flask.session.get('spotify_token')
    albums = user_albums(spotify_token)

    # GROUP ANALYSIS FUNCTION USES THE  liked_group_average() function
    final  = group_music_analysis(spotify_token, albums)

    # Add amount to total analyized
    flask.session['amount'] += final['ai']['amount']

    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if final['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(final['ai']['averageEmotion'].keys())
        emotionValues = [    final['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    final['song_title'] = USERNAME['display_name']
    final['song_artist_name'] = "Playlist Total Analyses"


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : final,
            'ai_response'  : ai_response,
            # 'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : final,
            # 'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)

# Playlist Analysis
@application.route('/playlist-analysis', methods=['GET'])
def playlist_analysis():

    # grab music
    spotify_token = flask.session.get('spotify_token')
    playlist_response = user_playlists(spotify_token)

    # GROUP ANALYSIS FUNCTION USES THE  liked_group_average() function
    final  = group_music_analysis(spotify_token, playlist_response)

    # Add amount to total analyized
    flask.session['amount'] += final['ai']['amount']


    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if final['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(final['ai']['averageEmotion'].keys())
        emotionValues = [    final['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    final['song_title'] = USERNAME['display_name']
    final['song_artist_name'] = "Playlist Total Analyses"


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : final,
            'ai_response'  : ai_response,
            # 'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : final,
            # 'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [final[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)




# INDIVISUAL GROUP DISPLAY
# Display all albums and links next to them to pictures of the album
@application.route('/indivisual-album-display', methods=['GET'])
def indivisualAlbumDisplay():

    # going to hold every album and their display data ['pictures'] , ['popularity'], ['name'] , ['uri']
    display_data = {
        'username' : flask.session['username'] 
    }

    # grab music
    spotify_token = flask.session.get('spotify_token')
    albums = user_albums(spotify_token)

    # gather pictures
    for album in albums:
        album_id = albums[album]["id"]
        data = fetch_spotify_data(spotify_token , f"https://api.spotify.com/v1/albums/{album_id}")

        # add to display data
        display_data[album] = {}
        display_data[album]['name'] = albums[album]['name']
        display_data[album]['id'] = album_id
        display_data[album]['pictures'] = data['images']
        display_data[album]['popularity'] = albums[album]['popularity']
        display_data[album]['amount'] = len(  albums[album]['songs']  )
        display_data[album]['release_date'] = data['release_date']
        display_data[album]['spotify_page'] = f"https://open.spotify.com/track/{album_id}"
        display_data[album]['songs'] = albums[album]['songs']




    # debug = fetch_spotify_data(spotify_token , f"https://api.spotify.com/v1/albums/5SKnXCvB4fcGSZu32o3LRY?si=17b25a68a03c497b")


    
    return flask.render_template('indivisual_group_listing.html' , display_data = display_data)

@application.route('/indivisual-playlist-display', methods=['GET'])
def indivisualPlaylistDisplay():
    # grab music
    spotify_token = flask.session.get('spotify_token')
    playlist_response = user_playlists(spotify_token)

    # going to hold every album and their display data ['pictures'] , ['popularity'], ['name'] , ['uri']
    display_data = {
        'username' : flask.session['username'] 
    }

    # gather pictures
    for pl in playlist_response:
        playlist_id = playlist_response[pl]["id"]
        data = fetch_spotify_data(spotify_token , f"https://api.spotify.com/v1/playlists/{playlist_id}")

        # add to display data
        display_data[ pl ] = {}
        display_data[ pl ]['name'] = playlist_response[pl]['name']
        display_data[ pl ]['id'] = playlist_id
        display_data[ pl ]['pictures'] = data['images']
        display_data[ pl ]['amount'] = len(  playlist_response[pl]['songs']  )
        display_data[ pl ]['spotify_page'] = f"https://open.spotify.com/playlist/{playlist_id}"
        display_data[ pl ]['popularity'] = f"{data['followers']['total']} listeners"
        display_data[ pl ]['songs'] =  playlist_response[pl]['songs']
        

        # PLAYLIST DATA DOESNT RETURN (fetch_album does)
        # display_data[ pl ]['release_date'] = data['release_date']

    return flask.render_template('indivisual_group_listing.html' , display_data = display_data)

# Playlist FINAL ANALYSIS
@application.route('/indivisual-album-analysis', methods=['POST'])
def indivisual_album_analysis():
    spotify_token = flask.session.get('spotify_token')



    # grab context from form POST  from /indivisual-playlist-display 
    user_form_args = flask.request.form
    # print(user_form_args)
    
    # display page passed in list of songs from the form
    music_list = flask.request.form.get('songs[]') 

    # convert string return from form into list
    music_list = ast.literal_eval(music_list)
    # music_list = music_list.strip('][').split(', ')


    # clean list into format that fits the liked_group_average() format
    for x in range(0 , len(music_list) , 1):
        # print(   music_list[x] )

        song_info = {
            "artists"  : music_list[x][2],
            "name"  :  music_list[x][1] ,
            "id"  :  music_list[x][0],
        }

        # replace music list with song info
        music_list[x] = song_info


    # this function returns two for parallel display of each (song) & grouped ai
    song_stats , each_song_stats = liked_group_average(spotify_token , music_list)
    
    # Add amount to total analyized
    flask.session['amount'] += song_stats['ai']['amount']

    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if song_stats['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
        emotionValues = [    song_stats['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = user_form_args["group_name"]


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : song_stats,
            'ai_response'  : ai_response,
            'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : song_stats,
            'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)

# Playlist FINAL ANALYSIS
@application.route('/indivisual-playlist-analysis', methods=['POST'])
def indivisual_playlist_analysis():
    spotify_token = flask.session.get('spotify_token')



    # grab context from form POST  from /indivisual-playlist-display 
    user_form_args = flask.request.form
    # print(user_form_args)
    
    # display page passed in list of songs from the form
    music_list = flask.request.form.get('songs[]') 

    # convert string return from form into list
    music_list = ast.literal_eval(music_list)
    # music_list = music_list.strip('][').split(', ')


    # clean list into format that fits the liked_group_average() format
    for x in range(0 , len(music_list) , 1):
        # print(   music_list[x] )

        song_info = {
            "artists"  : music_list[x][2],
            "name"  :  music_list[x][1] ,
            "id"  :  music_list[x][0],
        }

        # replace music list with song info
        music_list[x] = song_info


    # this function returns two for parallel display of each (song) & grouped ai
    song_stats , each_song_stats = liked_group_average(spotify_token , music_list)
    
    # Add amount to total analyized
    flask.session['amount'] += song_stats['ai']['amount']

    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if song_stats['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
        emotionValues = [    song_stats['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = user_form_args["group_name"]


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : song_stats,
            'ai_response'  : ai_response,
            'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : song_stats,
            'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)


# liked songs Analysis
@application.route('/liked-analysis', methods=['GET'])
def liked_analysis():
    spotify_token = flask.session.get('spotify_token')
    likes = user_likes(spotify_token)

    # this function returns two for parallel display of each (song) & grouped ai
    song_stats , each_song_stats = liked_group_average(spotify_token , likes)
    
    # Add amount to total analyized
    flask.session['amount'] += song_stats['ai']['amount']



    # GRAPHING

    # DATA POINTS FOR BAR GRAPH
    spotty_chart_datapoint_labels = [
        'danceability',
        'energy',
        'speechiness',
        'acousticness',
        # 'instrumentalness',
        'liveness',
        'valence',
    ]

    # PIE CHART
    ai_response = False
    if song_stats['ai'] is not None : 
        ai_response = True
        emotionsLabels = list(song_stats['ai']['averageEmotion'].keys())
        emotionValues = [    song_stats['ai']['averageEmotion'][i] for i in emotionsLabels  ]

    # No point to change as it is the same code as the song analysis from here to the components in html...
    USERNAME = fetch_spotify_data( spotify_token , 'https://api.spotify.com/v1/me' )
    song_stats['song_title'] = USERNAME['display_name']
    song_stats['song_artist_name'] = "❤"


    #kinda redundant but i mean.... why not have the modularity?
    if ai_response:
        content = {
            'stats'  : song_stats,
            'ai_response'  : ai_response,
            'each_song_stats'  : each_song_stats,

            # spotify data
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,

            # watson data
            'emotionLabels' : emotionsLabels,
            'emotionValues' : emotionValues,
        }

    #NO LYRICS
    else:
        content = {
            'stats'  : song_stats,
            'each_song_stats'  : each_song_stats,
            'ai_response'  : ai_response,
            'spotty_chart_labels' : spotty_chart_datapoint_labels    ,
            'spotty_chart_data' :  [song_stats[i] for i in spotty_chart_datapoint_labels   ]  ,
            # watson data
            'emotionLabels' : None,
            'emotionValues' : None,
        }


    # sessions for passed songs on html

    return flask.render_template('Liked_Group_analysis.html' , content = content)











# FLASK ERRORS
@application.errorhandler(404)
def page_not_found(e):
    try:
        meme_pic = fetch_meme('Look everyone!' , 'this guys lost...' )['data']['url']
        tag = f'<img src="{meme_pic}" alt="its a trap!">'
        return tag, 404
    except Exception as e:
        print("wtf happened with my meme???")
        print(e)
        return 'are u lost?', 404 

@application.errorhandler(500)
def handle_intsrverr(e):
    return flask.redirect('/Dashboard')







# SPOTIFY AND GENIUS AUTHORIZATIONS

#  Authorization by getting token
def authorize_spotify_NO_USER():
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{spotify_clientId}:{spotify_clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "client_credentials"


    r = requests.post(url, headers=headers, data=data).json()

    token = r['access_token']
    return token
def authorize_spotify_IMPLICIT(): 

    headers = {
        'client_id' : spotify_clientId,
        'response_type' : 'token',
        'redirect_uri' : spotify_callbackURL,
        'scope' : spotty_full_permission,
    }

    # open url on browser
    url = f"https://accounts.spotify.com/authorize?client_id={headers['client_id']}&response_type={headers['response_type']}&redirect_uri={headers['redirect_uri']}&scope={headers['scope']}"

    return url
def authorize_spotify_REFRESHABLE(): 

    headers = {
        'client_id' : spotify_clientId,
        'response_type' : 'code',
        'redirect_uri' : spotify_callbackURL,
        'scope' : spotty_full_permission,
    }

    # open url on browser
    url = f"https://accounts.spotify.com/authorize?client_id={headers['client_id']}&response_type={headers['response_type']}&redirect_uri={headers['redirect_uri']}&scope={headers['scope']}"
    return url
def _retrieve_refreshable_token(auth_code):
    # turn this into new function after user goes to web_page and logs in
    url = "https://accounts.spotify.com/api/token"
    headers = {}
    data = {}

    # Encode as Base64
    message = f"{spotify_clientId}:{spotify_clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "authorization_code"
    data['code'] = auth_code
    data['redirect_uri'] = spotify_callbackURL

    r = requests.post(url, headers=headers, data=data).json()
    token = r['access_token']
    return token
def _retrieve_genius_token(auth_code):
    # turn this into new function after user goes to web_page and logs in
    url = "https://api.genius.com/oauth/token"
    
    data = {}
    data['code'] = auth_code
    data['client_id'] = genius_clientId
    data['client_secret'] = genius_clientsECRET
    data['grant_type'] = "authorization_code"
    data['redirect_uri'] = genius_callbackURL
    data['response_type'] = 'code'

    r = requests.post(url, data=data).json()
    token = r['access_token']
    return token

# Genius 
def Oauth_function( base_url , CLIENT_ID , callback , scope ,  clientsECRET , res_type):
    url = f'{base_url}?client_id={CLIENT_ID}&redirect_uri={callback}&scope={scope}&response_type={res_type}&client_secret={clientsECRET}'

    return url



# SPOTIFFY ENDPOINTS
def fetch_spotify_data(token , endpoint ):
    headers = {"Authorization": "Bearer " + token}
    res = requests.get(url= endpoint ,  headers=headers ).json()
    if 'error' in res:
        print(f"\n{flask.request.remote_addr} -------\nERROR {res['error']['message']} \n")
        flask.session['spotify_expired'] = True
        return f"ERROR"
        # return flask.redirect(flask.url_for('Dashboard', Authorization= f'Bearer {token}' ))
    return res





# grab music groups
def user_likes(token):
   
    # LOOKUP SONGS
    # headers = {"Authorization": "Bearer " + token}
    results = fetch_spotify_data(token , 'https://api.spotify.com/v1/me/tracks' )
    all_songs = []
    totalLikedSongs = int(results['total'])
    while results:   
        for idx, item in enumerate(results['items']):
            track = item['track']
            song_info = {
                "artists"  : [  track['artists'][i]['name']  for i in range(len(track['artists']))  ],
                "name"  :  track['name'] ,
                "id"  :  track['id'],
                "popularity"  :  track['popularity']
            }
            all_songs.append( song_info )
       
        #next page check
        if results['next']: 
            results = fetch_spotify_data(token , results['next'] )
        else:
            results = None

    return all_songs
def user_albums(token):
    playlistUrl = f"https://api.spotify.com/v1/me/albums"
    headers = {"Authorization": "Bearer " + token}
    results = requests.get(url=playlistUrl, headers=headers).json()

    # GRAB ALBUMS
    all_albums = {}
    count = 0
    while results:  
        for item in results['items']:
            album = item['album']
            all_albums[count] =  {
                'name' : item['album']['name'],
                "genres" : album['genres'],
                "id" : album['id'],
                "popularity" : album['popularity'],
                "songs" : [],
            }
            # ADD SONGS
            for track in item['album']['tracks']['items']:
                all_albums[count]['songs'].append(   (track['id'] , track['name']    ,  [i['name'] for i in track['artists']  ]  )   )
            count += 1

        if results['next']: #next page check
            results = requests.get(url=results['next'], headers=headers).json()
        else:
            results = None
    
    
    
    return all_albums
def user_playlists(token):
    playlistUrl = f"https://api.spotify.com/v1/me/playlists"
    headers = {"Authorization": "Bearer " + token}
    results = requests.get(url=playlistUrl, headers=headers).json()

    all_playlists = {}
    count = 0
    # EVERY PLAYLIST
    while results:   
        for item in results['items']:
            all_playlists[count] =  {
                'owner' : item['owner']['display_name'],
                'name' : item['name'],
                "description" : item['description'],
                "id" : item['id'],
                "songs" : [],
            }

            # LOOKUP SONGS
            pl_tracks_call = requests.get(url=item['tracks']['href'] , headers = headers).json()
            while pl_tracks_call:
                for track in pl_tracks_call['items']:
                    all_playlists[count]['songs'].append(   (track['track']['id'] , track['track']['name']  ,[ i['name'] for i in track['track']['artists']  ] )   )
            
                # PAGINATION [TRACKS]
                if pl_tracks_call['next']:
                    pl_tracks_call = requests.get(url=pl_tracks_call['next'] , headers = headers).json()
                else:
                    pl_tracks_call = None
            
            count += 1

         # PAGINATION [PLAYLISTS]
        if results['next']:
            results = requests.get(url=item['next'] , headers = headers).json()
        else:
            results = None
    return all_playlists






# song AI  analysis 
def _song_analysis_details(token , song_id , details : bool , song_title , artist_name): 

    # check if song in database already
    with open('song_db.json' , "r") as db:
        loaded = json.load(db)
        if song_id in loaded:
            return loaded[song_id]






    endpoint = f"https://api.spotify.com/v1/audio-features/{song_id}"
    titleInfo = fetch_spotify_data(token, f'https://api.spotify.com/v1/tracks/{song_id}')
    song_title =  titleInfo['name']  
    artist_name =  titleInfo['artists'][0]['name']

    # fetch data
    res = fetch_spotify_data(token , endpoint )

    # SONG DETAIL DOUBLE FEATURE of the function
    if details:
        analysis = requests.get( url = res['analysis_url'], headers = headers ).json()
        pprint.pprint( analysis.keys()  );print("\n")
        pprint.pprint( analysis['track']   )
        return analysis


    # check if response was a dictionary
    if isinstance(res , dict):
        pass
    else:
        return None
    


    # API COOL DOWN ERROR HANDLING
    while 'error' in res.keys():
        print(f'< {song_id} > got an error\n waiting for api cooldown')
        time.sleep(API_COOLDOWN_RATE)
        res = _song_analysis_details(token, song_id , details  )
    
    
    
    # append WATSON AI to SOTIFY results  (master dictionary of clean watson frequencies)
    res['ai'] = _watson_lyric_analysis( song_title, artist_name)
    res['song_title'] = song_title
    res['artist_name'] = artist_name



    # adding items to song_db.json DATABASE
    with open('song_db.json' , 'r') as  db :
        loaded = json.load( db )
        loaded[song_id] = res
    with open('song_db.json' , 'w') as  db :
        db .write(  json.dumps(loaded)   )

    return res

def _watson_lyric_analysis(  song_title, artist_name):
    print(f"\nAnalyzing {artist_name} : {song_title}")
    genius_token = flask.session.get("genius_token")
    lyrics = _request_song_info(genius_token , song_title , artist_name )

    # NLU
    song_ai = []
    nlu = None
    if lyrics:
        # INSTEAD OF GRABBING AI RESPONSE FOR EACH BAR... JUST RUN THE WHOLE LYRIC STRING
        watson_input = ""
        try:
            # APPEND LYRICS
            for bar in lyrics:
                watson_input += f"{bar} "
            # GET WATSON INFO
            nlu = watson.ai_to_Text( watson_input )
            # AVERAGE CALC IS RETURNING CLEAN DATA by reading an array,
            # WE PLACE ONE ITEM IF WE DECIDE TO RUN LYRICS AS ONE
            nlu =  watson.averages_calc(   [  nlu  ]   )

        except Exception as e:
            nlu = None
            print(f'\n\nWATSON API ERROR: {e}\n\n\n{watson_input}\n')
    else:
        print("No lyrics found\n")

    context = {
        'lyrics' : lyrics,
        'nlu' : nlu,
        # 'tone' : tone
    }
    return context

def _request_song_info(token , song_title, artist_name):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + token  }
    search_url = base_url + '/search'
    data = {'q': song_title + ' ' + artist_name}
    response = requests.get(search_url, data=data, headers=headers).json()

    # Search for matches in the request response
    remote_song_info = None
    for hit in response['response']['hits']:
        if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break

    # Extract lyrics from URL if the song was found
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        return _webcrawl_lyrics(song_url)
    else:
        return None

def _webcrawl_lyrics(url):
    # EXTRACT HTML
    page = requests.get(url)
    html = bs4.BeautifulSoup(page.text, 'html.parser')

    try:
        lyrics = html.find("div", {"id": "lyrics-root-pin-spacer"}).get_text()
    except Exception as e:
        print(  '\ndef _webcrawl_lyrics(url):\nERROR FINDING LYRICS: ' , str(e))
        return None

    
    # CREATE ARRAY THAT FINDS A LOWER CASE AND AN UPPERCASE RIGHT NEXT TO EACHOTHER AND SPLITS STRING
    lyrics_text = str(lyrics)
    all_bars = []
    br_point = 0
    previous = 0
    for x in range(0, len(lyrics_text)  - 1 , 1)  :
        if  lyrics_text[x].islower() and lyrics_text[x+1].isupper():
            br_point = x+1
            bar = lyrics_text[previous:br_point]
            all_bars.append(bar)
            previous = br_point
        

    # removing "[ SONG EVENT ]" from each bar
    event_start = None
    event_end = None
    for x in all_bars:
        found = False
        for y in range(len(x)):
            if x[y] == '['  : event_start = y  
            if x[y] == ']'  :
                found = True
                event_end = y
                no_event_bar = x[:event_start] + ' ' + x[event_end+1:]
        if found:
            x = no_event_bar

    # clean lyrics string
    if "Share URLCopy" in all_bars:
        all_bars.remove('Share URLCopy')
    if "1Embed" in all_bars:
        all_bars.remove('1Embed')
    if all_bars[-1] == "Embed":
        all_bars.pop(-1)
    if len(all_bars) <= 3:
        all_bars = None

    return all_bars




# music group analysis

def group_music_analysis(token , group:dict() ):
    final  = {
        'acousticness' : [],
        'danceability' : [],
        'duration_ms' : [],
        'energy' : [],
        'instrumentalness' : [],
        'liveness' : [],
        'loudness' : [],
        'speechiness' : [],
        'tempo' : [],
        'valence' : [],
        'ai' : []
    }

    # songs found by WATSON
    watson_arr = []

    for album in group:
        print("\n\n--------" ,  group[album]["name"] , "------"  )
        for song in group[album]['songs']:
            song_id = song[0]
            song_name = song[1]
            song_artists = song[2] #main artist is item number 0
            analysis = _song_analysis_details(token,  song_id , False ,  song_name , song_artists[0] )
            
            # check if response returned a dictionary
            if isinstance(analysis , dict):
                pass
            else:
                print('\n----- DEBUG -----\n------ group_music_analysis(token , group:dict() ) --------')
                print("Spotify returned a Response type instead of JSON")
                continue


            # populates all songs into final song_stat variable
            for x in final.keys():
                final[x].append(analysis[x])
                
            # check if watson ai
            if analysis['ai']['nlu'] is not None:
                print("☁☁☁")
                watson_arr.append(  (analysis['song_title'] , analysis['artist_name']  )   )



    # AVERAGING  SPOTIFY  #every key except ["ai"]
    spotty_keys = list(final.keys())[:-1]
    for attribute in spotty_keys:
        final[attribute] =  statistics.mean(final[attribute])
    


    # ----------------AVERAGING WATSON for FINAL ["ai"]   --------------------
    group_merge_ai = {}

    # CHECKING FOR PROPER nlu DICTIONARY && creating merged dict...
    solid_nlu = False
    for x in range(  len(final['ai'])   ):
        if final['ai'][x]['nlu'] is not None :
            solid_nlu = True
            good_dict = final['ai'][x]['nlu']
            break
    if solid_nlu:
        for key in good_dict :
            if key =='averageEmotion':
                group_merge_ai[key] = []
                continue
            group_merge_ai[key] = {}
            for inner_keys in good_dict[key]:
                group_merge_ai[key][inner_keys] = []
    else: #IMPORTANT CATCH IF NO AI
        final['ai'] = None
        return final 


    # # # DEBUG
    # with open("group_merge_ai.json" , "a") as output:
    #     json.dump(group_merge_ai, output, indent = 2)


    # merge all values in NLU into group_merge_ai
    for x in range( 0 ,   len(final['ai'])   ,   1  ):
        NLU = final['ai'][x]['nlu']
        
        # APPEND ALL WATSON DATA INTO group_merge_ai , otherwise ignore it and move on
        if NLU is not None :
            # append all group emotions ------> EMOTIONS
            group_merge_ai['averageEmotion'].append(NLU['averageEmotion'])

            # create dict keys for all concept frequencies  ------> CONCEPTS
            singularities = []
            for i in NLU['conceptfrequencies']:
                # Singular keys found with empty arr
                if len( NLU['conceptfrequencies'][i] ) < 1:
                    print("DEBUG full group: singularity:   ", i)
                    singularities.append(i)
                    continue
                # if there the key already exists!
                if i in group_merge_ai['conceptfrequencies']:
                    # ITERATE THROUGH NLU['conceptfrequencies'][i]
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
                else:
                    # if the concept is not in the dictionary as a key... add it with it's coentents as well
                    # print(NLU['conceptfrequencies'][i] )
                    group_merge_ai['conceptfrequencies'][i] = []
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
            NLU['conceptfrequencies']['singularities'] = singularities


            # goes through dictionary and populates the merge
            for key in NLU.keys():
                if key == "averageEmotion" or  key == "conceptfrequencies":
                    continue
                for i in NLU[key]:
                    if isinstance(NLU[key][i], int):
                        if  i  in group_merge_ai[key]:
                            if isinstance(group_merge_ai[key][i], list):
                                group_merge_ai[key][i] = 1
                            else:
                                group_merge_ai[key][i] +=  NLU[key][i]
                        else:
                             group_merge_ai[key][i] = NLU[key][i]
                    else:
                        # print( group_merge_ai[key][i]  ) #/// VARIALE IN QUESION!
                        if i  in group_merge_ai[key]:
                            group_merge_ai[key][i].extend(  NLU[key][i]    )
                        else:
                            group_merge_ai[key][i] = NLU[key][i]

    # OVER ALL EMOTION AVERAGE
    temp = {
        "Anger": [],
        "Disgust": [],
        "Fear": [],
        "Joy": [],
        "Sadness": []
      }
    for x in  range( 0 , len(group_merge_ai['averageEmotion'])  ,   1 ):
        for key in group_merge_ai['averageEmotion'][x]:
            temp[key].append(group_merge_ai['averageEmotion'][x][key])
    # replace vars 
    for emotion in temp:
        temp[emotion] = statistics.mean(temp[emotion])


    # LISTS BECOMES MERGED DICTIONARIES
    group_merge_ai['amount'] = len(group_merge_ai['averageEmotion']) #FIND AMOUNT OF ANALYZED SONGS  
    group_merge_ai['averageEmotion'] = temp
    final['ai'] = group_merge_ai
    
    # remember watson_arr? 
    final['ai']['watson_songs'] = watson_arr
    


    # # DEBUG
    # with open("final.json" , "a") as output:
    #     json.dump(final, output, indent = 2)

    return final 

def liked_group_average(token , group : list()  ): 

    #  -------   spotify OUTPUT VARIABLES    -------
    # populate song arr
    song_stats  = {
        'acousticness' : [],
        'danceability' : [],
        'duration_ms' : [],
        'energy' : [],
        'instrumentalness' : [],
        'liveness' : [],
        'loudness' : [],
        'speechiness' : [],
        'tempo' : [],
        'valence' : [],
        'ai' : []
    }
    # populating song_stats arrays with song stats.
    each_song_stats = {}

    # WATSON ai found songs
    watson_arr = []
    
    # iterate through each sonf in group ----> (group is a list)
    for song in group :
        name = song['name']
        song_id = song['id']
        # Song == a specific song's clean data //phase 0
        song = _song_analysis_details(token, song_id , False ,  name , song['artists'][0] )
        # append data to keys of 
        for x in song_stats.keys():
            song_stats[x].append(song[x])
       

        # ADD FINAL SONG PRODUCT as a key in each_song_stats
        each_song_stats[name] = song

        # check if watson ai
        if song['ai']['nlu'] is not None:
            print("☁")
            watson_arr.append(  ( song['song_title'] , song['artist_name'] )    )


 
 
    #    DEBUG
        # each_song_stats[song_id] = song
        # print(each_song_stats[name]['id'])




    # ****************
    # AT THIS POINT song_stats is a dictionary that holds arrays populated with all the user's liked music
    # this is to analyse the average of the whole playlist
    # ****************



    # averaging spotify (turning each key into it's average)
    spotty_keys = list(song_stats.keys())[:-1]  #every key except ["ai"]
    for x in spotty_keys:
        song_stats[x] =  statistics.mean(song_stats[x])




    # averaging watson    ["ai"]
    #  -------  watson  OUTPUT VARIABLES    -------
    group_merge_ai = {}

    # CHECKING FOR PROPER nlu DICTIONARY && creating merged dict...
    solid_nlu = False
    for x in range(len(song_stats['ai'])):
        if song_stats['ai'][x]['nlu'] :
            solid_nlu = True
            good_dict = x
            break
    if solid_nlu:
        for key in song_stats['ai'][x]['nlu']:
            if key =='averageEmotion':
                group_merge_ai[key] = []
                continue
            group_merge_ai[key] = {}
            for inner_keys in song_stats['ai'][x]['nlu'][key]:
                group_merge_ai[key][inner_keys] = []
    else: #IMPORTANT CATCH IF NO AI
        song_stats['ai'] = None

        return song_stats , each_song_stats

    #    NLU IS EACH ITEM IN THE SONG_STATS['ai']  ---> which needs to become a grouped dict of lists avg!!!!!


    # iterate through every SONG TEXT and grab nlu
    # merge all values in NLU into group_merge_ai
    for x in range( 0 ,   len(song_stats['ai'])   ,   1  ):
        NLU = song_stats['ai'][x]['nlu']

        if NLU is not None :
            # append all group emotions ------> EMOTIONS
            group_merge_ai['averageEmotion'].append(NLU['averageEmotion'])

            # create dict keys for all concept frequencies  ------> CONCEPTS
            singularities = []
            for i in NLU['conceptfrequencies']:
                # Singular keys found with empty arr
                if len( NLU['conceptfrequencies'][i] ) < 1:
                    # print("DEBUG: singularity:   ", i)
                    singularities.append(i)
                    continue
                # if there the key already exists!
                if i in group_merge_ai['conceptfrequencies']:
                    # ITERATE THROUGH NLU['conceptfrequencies'][i]
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
                else:
                    # if the concept is not in the dictionary as a key... add it with it's coentents as well
                    # print(NLU['conceptfrequencies'][i] )
                    group_merge_ai['conceptfrequencies'][i] = []
                    for concept in NLU['conceptfrequencies'][i]:
                        if isinstance(concept, str):
                            group_merge_ai['conceptfrequencies'][i].append(concept)
                        elif isinstance(concept, list):
                            for inner_concept in concept:
                                group_merge_ai['conceptfrequencies'][i].append(inner_concept)
            NLU['conceptfrequencies']['singularities'] = singularities


            # goes through dictionary and populates the merge
            for key in NLU.keys():
                if key == "averageEmotion" or  key == "conceptfrequencies":
                    continue
                for i in NLU[key]:
                    if isinstance(NLU[key][i], int):
                        if  i  in group_merge_ai[key]:
                            if isinstance(group_merge_ai[key][i], list):
                                group_merge_ai[key][i] = 1
                            else:
                                group_merge_ai[key][i] +=  NLU[key][i]
                        else:
                             group_merge_ai[key][i] = NLU[key][i]
                    else:
                        # print( group_merge_ai[key][i]  ) #/// VARIALE IN QUESION!
                        if i  in group_merge_ai[key]:
                            group_merge_ai[key][i].extend(  NLU[key][i]    )
                        else:
                            group_merge_ai[key][i] = NLU[key][i]






    # Average all emotions in array
    # OVER ALL EMOTION AVERAGE
    temp = {
        "Anger": [],
        "Disgust": [],
        "Fear": [],
        "Joy": [],
        "Sadness": []
      }
    for x in  range( 0 , len(group_merge_ai['averageEmotion'])  ,   1 ):
        for key in group_merge_ai['averageEmotion'][x]:
            temp[key].append(group_merge_ai['averageEmotion'][x][key])
    # replace vars 
    for emotion in temp:
        temp[emotion] = statistics.mean(temp[emotion])




    # LISTS BECOMES MERGED DICTIONARIES
    group_merge_ai['amount'] = len(group_merge_ai['averageEmotion']) #FIND AMOUNT OF ANALYZED SONGS  
    group_merge_ai['averageEmotion'] = temp
    song_stats['ai'] = group_merge_ai

    
    
    # remember watson_arr?
    song_stats['ai']['watson_songs'] = watson_arr
    
    return song_stats , each_song_stats



# helper functions
def fetch_meme(text0 , text1):
    userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'


    #fetch all memes
    data = requests.get('https://api.imgflip.com/get_memes').json()['data']['memes']
    #List top memes with 2 text slots
    images = [{'name':image['name'],'url':image['url'],'id':image['id']} for image in data if image['box_count'] == 2]


    #Take input from user -- Meme, Text0 and Text1
    id = random.randint(1,100)


    #generated meme
    URL = 'https://api.imgflip.com/caption_image'
    params = {
        'username':meme_username,
        'password':meme_password,
        'template_id':images[id-1]['id'],
        'text0':text0,
        'text1':text1
    }
    response = requests.request('POST',URL,params=params).json()
    return response




# application.run(host = '0.0.0.0' , port = 8080)
application.run( port = 8080)


