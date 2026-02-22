from flask import Flask, render_template, request
import pickle
import numpy as np
import os

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


# ---------------- HOME PAGE ----------------
@app.route("/")
def index():
    try:
        return render_template(
            "index.html",
            book_name=list(popular_df["Book-Title"].values),
            author=list(popular_df["Book-Author"].values),
            image=list(popular_df["Image-URL-M"].values),
            votes=list(popular_df["num_ratings"].values),
            ratings=list(popular_df["avg_ratings"].values),
        )
    except Exception as e:
        return f"Error rendering homepage: {str(e)}"


# ---------------- RECOMMEND PAGE UI ----------------
@app.route("/recommend")
def recommend_ui():
    return render_template("recommend.html")


# ---------------- RECOMMEND LOGIC ----------------
@app.route("/recommend_books", methods=["POST"])
def recommend():
    try:
        user_input = request.form.get("user_input")

        if not user_input or user_input not in pt.index:
            return render_template("recommend.html", data=[])

        index = np.where(pt.index == user_input)[0][0]

        similar_items = sorted(
            list(enumerate(similarity_score[index])),
            key=lambda x: x[1],
            reverse=True,
        )[1:5]

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

    except Exception as e:
        return f"Error generating recommendations: {str(e)}"


# ---------------- PRODUCTION ENTRY ----------------
# DO NOT use debug=True in production
if __name__ == "__main__":
    app.run()