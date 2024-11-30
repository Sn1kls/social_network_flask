from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from datetime import datetime
from pydantic import ValidationError
from models import UserCreate, UserUpdate, PostCreate  # Імпортуємо моделі з models.py

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/social_network"
mongo = PyMongo(app)
users_collection = mongo.db.users
users_collection.create_index('email', unique=True)  # Додаємо індекс для email

posts_collection = mongo.db.posts
posts_collection.create_index('post_id', unique=True)  # Додаємо індекс для post_id


@app.route('/create_user_form')
def create_user_form():
    return render_template('create_user.html')


@app.route('/create_user', methods=['POST'])
def create_user():
    try:
        # Валідація даних через Pydantic
        data = UserCreate(
            name=request.form.get('name'),
            email=request.form.get('email'),
            bio=request.form.get('bio', ''),
            following=request.form.getlist('following')
        )

        # Перевірка унікальності email
        if users_collection.find_one({'email': data.email}):
            return jsonify({'error': 'Email already exists'}), 400

        # Створення нового користувача
        new_user = {
            'name': data.name,
            'email': data.email,
            'bio': data.bio,
            'created_at': datetime.utcnow(),
            'following': data.following
        }
        users_collection.insert_one(new_user)
        return redirect(url_for('get_users'))
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400


@app.route('/users', methods=['GET'])
def get_users():
    users = users_collection.find()  # Отримуємо всіх користувачів з MongoDB
    return render_template('users_list.html', users=users)  # Передаємо користувачів у шаблон


@app.route('/edit_user/<user_id>', methods=['GET'])
def edit_user_form(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Передача даних користувача у форму
    return render_template('edit_user.html', user=user)


@app.route('/update_user/<user_id>', methods=['POST'])
def update_user(user_id):
    try:
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Валідація через Pydantic
        data = UserUpdate(
            name=request.form.get('name'),
            email=request.form.get('email'),
            bio=request.form.get('bio', ''),
            following=request.form.getlist('following')
        )

        # Перевірка унікальності email
        if users_collection.find_one({'email': data.email, '_id': {'$ne': ObjectId(user_id)}}):
            return jsonify({'error': 'Email already exists'}), 400

        # Оновлення користувача
        updated_fields = {
            'name': data.name,
            'email': data.email,
            'bio': data.bio,
            'following': data.following
        }
        users_collection.update_one({'_id': ObjectId(user_id)}, {'$set': updated_fields})
        return redirect(url_for('get_users'))
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400


@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    result = users_collection.delete_one({'_id': ObjectId(user_id)})
    if result.deleted_count == 0:
        return jsonify({'error': 'User not found'}), 404
    return redirect(url_for('get_users'))


@app.route('/create_post_form', methods=['GET'])
def create_post_form():
    return render_template('create_post.html')


@app.route('/create_post', methods=['POST'])
def create_post():
    try:
        # Валідація даних через Pydantic
        data = PostCreate(
            post_id=request.form.get('post_id'),
            user_id=request.form.get('user_id'),
            content=request.form.get('content'),
            likes=request.form.getlist('likes'),
            comments=[]  # Коментарі поки залишаються порожніми
        )

        # Перевірка унікальності post_id
        if posts_collection.find_one({'post_id': data.post_id}):
            return jsonify({'error': 'Post with this ID already exists'}), 400

        # Створення нового поста
        new_post = data.dict()
        posts_collection.insert_one(new_post)
        return redirect(url_for('create_post_form'))
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400


@app.route('/posts', methods=['GET'])
def get_posts():
    posts = posts_collection.find()  # Отримуємо всі пости з MongoDB
    return render_template('posts_list.html', posts=posts)  # Передаємо пости у шаблон
