from flask import Flask, render_template, request
import pickle
import numpy as np
import os
import random

app = Flask(__name__)

# ---------------- SAFE PICKLE LOADER ----------------
def load_pickle(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filename} not found in project root.")
    with open(filepath, "rb") as f:
        return pickle.load(f)


# ---------------- LOAD DATA FILES ----------------
try:
    popular_df = load_pickle("popular.pkl")
    pt = load_pickle("pt.pkl")
    books = load_pickle("books.pkl")
    similarity_score = load_pickle("similarity_score.pkl")

except Exception as e:
    print("Error loading pickle files:", e)
    raise e


# ---------------- CREATE CASE-INSENSITIVE LOOKUP ----------------
# This solves small/uppercase typing issue
pt_index_lookup = {title.lower(): title for title in pt.index}


# ---------------- HOME PAGE ----------------
@app.route("/")
def index():
    return render_template(
        "index.html",
        book_name=list(popular_df["Book-Title"].values),
        author=list(popular_df["Book-Author"].values),
        image=list(popular_df["Image-URL-M"].values),
        votes=list(popular_df["num_ratings"].values),
        ratings=[round(x, 2) for x in popular_df["avg_ratings"].values],
    )


# ---------------- RECOMMEND PAGE UI ----------------
@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html")


# ---------------- RECOMMEND LOGIC ----------------
@app.route("/recommend_books", methods=["POST"])
def recommend():

    user_input = request.form.get("user_input")

    if not user_input:
        return render_template("recommend.html", data=[])

    # Normalize input (case insensitive)
    user_input = user_input.strip().lower()

    # 🔹 FALLBACK if book not found
    if user_input not in pt_index_lookup:

        data = []

        # random 5 popular books
        random_books = popular_df.sample(5)

        for _, row in random_books.iterrows():
            item = [
                row["Book-Title"],
                row["Book-Author"],
                row["Image-URL-M"],
            ]
            data.append(item)

        return render_template("recommend.html", data=data)

    # 🔹 COLLABORATIVE FILTERING
    actual_title = pt_index_lookup[user_input]

    index = np.where(pt.index == actual_title)[0][0]
    distances = similarity_score[index]

    similar_items = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True,
    )[1:6]

    data = []

    for i in similar_items:
        temp_df = books[books["Book-Title"] == pt.index[i[0]]]

        if not temp_df.empty:
            item = [
                temp_df["Book-Title"].values[0],
                temp_df["Book-Author"].values[0],
                temp_df["Image-URL-M"].values[0],
            ]
            data.append(item)

    return render_template("recommend.html", data=data)


# ---------------- PRODUCTION ENTRY ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)