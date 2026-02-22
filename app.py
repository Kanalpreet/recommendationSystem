from flask import Flask, render_template, request
import pickle
import numpy as np

app = Flask(__name__)

# Load files safely
with open('popular.pkl', 'rb') as f:
    popular_df = pickle.load(f)

with open('pt.pkl', 'rb') as f:
    pt = pickle.load(f)

with open('books.pkl', 'rb') as f:
    books = pickle.load(f)

with open('similarity_score.pkl', 'rb') as f:
    similarity_score = pickle.load(f)


@app.route('/')
def index():
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        ratings=list(popular_df['avg_ratings'].values)
    )


@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')

    if user_input not in pt.index:
        return render_template('recommend.html', data=[])

    index = np.where(pt.index == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_score[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:5]

    data = []

    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item = [
            temp_df['Book-Title'].values[0],
            temp_df['Book-Author'].values[0],
            temp_df['Image-URL-M'].values[0]
        ]
        data.append(item)

    return render_template('recommend.html', data=data)