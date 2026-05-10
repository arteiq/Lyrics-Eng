from flask import Flask, request, render_template, session, redirect, url_for
import json
import lyricsgenius

app = Flask(__name__)
app.secret_key = '7563874123'

genius_token = 'Lxx6UoRvGE-IS77CF2Zkk7h5FgQQW-a7dyctI3PS668K6dXYnhxu_l9gqDJHQklq'
genius = lyricsgenius.Genius(genius_token, timeout=10, remove_section_headers=True, skip_non_songs=True)

db = 'users.json'
users = {}
try:
    with open(db, 'r') as f:
        users = json.load(f)
except FileNotFoundError:
    users = {}


def search_and_get_lyrics(song_title, artist_name=None):
    genius.excluded_terms = ["(Remix)", "(Live)"]
    try:
        if artist_name:
            song = genius.search_song(song_title, artist_name)
        else:
            song = genius.search_song(song_title)
        if song:
            song_dict = song.to_dict()
            print(song_dict)
            song_info = {
                'title': song.title if song_title else 'Неизвестно',
                'full_title': song.full_title if song.full_title else 'Неизвестно',
                'artist': song.artist,
                'album': song_dict.get('album', {}).get('name') if song_dict.get('album', {}).get('name')
                else 'Неизвестно',
                'song_art_image': song.song_art_image_url if song.song_art_image_url else "",
                'year': song_dict.get('release_date_for_display') if song_dict.get('release_date_for_display')
                else 'Неизвестно',
            }
            return song.lyrics, song_info
        else:
            return "Песня не найдена.", None
    except Exception as e:
        return f"Ошибка: {e}", None


@app.route('/register', methods=['GET', 'POST'])
def register():
    global users
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            error = 'Это имя уже занято.'
            return render_template('register.html', error=error)

        users[username] = password
        with open(db, 'w') as f:
            json.dump(users, f)

        session['username'] = username
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            if users[username] == password:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                error = 'Неверный пароль.'
                return render_template('login.html', error=error)
        else:
            error = 'Имя не найдено. Зарегистрируйтесь.'
            return render_template('login.html', error=error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    lyrics = ''
    song_title = ''
    artist_name = ''
    song_info = None
    user = session.get('username')

    if request.method == 'POST':
        song_title = request.form['song']
        artist_name = request.form['artist']
        lyrics, song_info = search_and_get_lyrics(song_title, artist_name)

    return render_template('index.html', lyrics=lyrics, song=song_title, artist=artist_name, song_info=song_info,
                           user=user)


if __name__ == '__main__':
    app.run(debug=True)