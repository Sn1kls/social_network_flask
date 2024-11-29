from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['social_network']
users_collection = db['Users']
posts_collection = db['Posts']


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        bio = request.form['bio']
        created_at = datetime.now()
        # Додаємо нового користувача
        users_collection.insert_one({
            "name": name,
            "email": email,
            "bio": bio,
            "created_at": created_at,
            "following": []
        })
        return redirect(url_for('index'))

    users = users_collection.find()
    return render_template('index.html', users=users)


@app.route("/<user_id>/posts", methods=["GET", "POST"])
def posts(user_id):
    if request.method == "POST":
        content = request.form['content']
        created_at = datetime.now()
        posts_collection.insert_one({
            "user_id": user_id,
            "content": content,
            "likes": [],
            "comments": [],
            "created_at": created_at
        })
        return redirect(url_for('posts', user_id=user_id))

    posts = posts_collection.find({"user_id": user_id})
    return render_template('posts.html', posts=posts, user_id=user_id)


@app.route("/<user_id>/follow", methods=["POST"])
def follow(user_id):
    current_user_id = request.form['current_user_id']
    users_collection.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$push": {"following": user_id}}
    )
    return redirect(url_for('index'))


@app.route("/post/<post_id>/like", methods=["POST"])
def like_post(post_id):
    user_id = request.form['user_id']
    posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"likes": user_id}}
    )
    return redirect(url_for('posts', user_id=user_id))


@app.route("/post/<post_id>/comment", methods=["POST"])
def comment_on_post(post_id):
    user_id = request.form['user_id']
    content = request.form['content']
    created_at = datetime.now()
    comment_id = ObjectId()  # Генерація нового ID для коментаря
    posts_collection.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": {
            "comment_id": comment_id,
            "user_id": user_id,
            "content": content,
            "created_at": created_at
        }}}
    )
    return redirect(url_for('posts', user_id=user_id))


@app.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    users_collection.delete_one({"_id": ObjectId(user_id)})
    posts_collection.delete_many({"user_id": user_id})  # Видалення постів користувача
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
