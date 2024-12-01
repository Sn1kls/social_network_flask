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


@app.route('/edit_post/<post_id>', methods=['GET'])
def edit_post_form(post_id):
    post = posts_collection.find_one({'post_id': post_id})
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    # Передаємо дані поста в шаблон для редагування
    return render_template('edit_post.html', post=post)


@app.route('/update_post/<post_id>', methods=['POST'])
def update_post(post_id):
    post = posts_collection.find_one({'post_id': post_id})
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    # Отримуємо оновлені дані з форми
    content = request.form.get('content')
    likes = request.form.getlist('likes')

    # Оновлюємо пост
    updated_fields = {
        'content': content,
        'likes': likes
    }
    posts_collection.update_one({'post_id': post_id}, {'$set': updated_fields})
    return redirect(url_for('get_posts'))


@app.route('/delete_post/<post_id>', methods=['POST'])
def delete_post(post_id):
    result = posts_collection.delete_one({'post_id': post_id})
    if result.deleted_count == 0:
        return jsonify({'error': 'Post not found'}), 404
    return redirect(url_for('get_posts'))


@app.route('/insert_users_form', methods=['GET'])
def insert_users_form():
    # Відображаємо форму для вставки користувачів
    return render_template('insert_users.html')


@app.route('/insert_users', methods=['POST'])
def insert_users():
    # Вставляємо тестових користувачів
    test_users = [
        {
            'name': 'Alice',
            'email': 'alice@example.com',
            'bio': 'Loves coding',
            'created_at': datetime.utcnow(),
            'following': []
        },
        {
            'name': 'Bob',
            'email': 'bob@example.com',
            'bio': 'Data enthusiast',
            'created_at': datetime.utcnow(),
            'following': []
        },
        {
            'name': 'Charlie',
            'email': 'charlie@example.com',
            'bio': 'Tech blogger',
            'created_at': datetime.utcnow(),
            'following': []
        }
    ]
    users_collection.insert_many(test_users)
    return redirect(url_for('get_users'))  # Переходимо до списку користувачів


@app.route('/insert_posts_form', methods=['GET'])
def insert_posts_form():
    # Відображаємо форму для вставки постів
    return render_template('insert_posts.html')


@app.route('/insert_posts', methods=['POST'])
def insert_posts():
    # Видаляємо всі пости перед додаванням нових тестових постів
    posts_collection.delete_many({})

    # Вставляємо тестові пости
    test_posts = [
        {
            'post_id': '1',
            'user_id': 'Alice',
            'content': 'This is my first post!',
            'likes': [],
            'comments': []
        },
        {
            'post_id': '2',
            'user_id': 'Bob',
            'content': 'Data is the new oil.',
            'likes': [],
            'comments': []
        },
        {
            'post_id': '3',
            'user_id': 'Charlie',
            'content': 'Tech trends of 2024.',
            'likes': [],
            'comments': []
        }
    ]

    # Додаємо пости в колекцію
    for post in test_posts:
        # Перевіряємо, чи існує пост з таким post_id, щоб уникнути дублювання
        if not posts_collection.find_one({'post_id': post['post_id']}):
            posts_collection.insert_one(post)

    # Переходимо до списку постів
    return redirect(url_for('get_posts'))


@app.route('/add_follower_form/<user_id>', methods=['GET'])
def add_follower_form(user_id):
    return render_template('add_follower.html', user_id=user_id)


@app.route('/add_follower/<user_id>', methods=['POST'])
def add_follower(user_id):
    follower_id = request.form.get('follower_id')
    if not follower_id:
        return jsonify({'error': 'Follower ID is required'}), 400

    # Оновлення масиву підписників
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$addToSet': {'following': follower_id}}  # Додає, якщо підписник ще не доданий
    )
    return redirect(url_for('get_users'))  # Повернення до списку користувачів


@app.route('/add_comment_form/<post_id>', methods=['GET'])
def add_comment_form(post_id):
    # Отримуємо пост для передачі в шаблон
    post = posts_collection.find_one({'post_id': post_id})
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    # Відображаємо шаблон форми для додавання коментаря
    return render_template('add_comment.html', post=post)


@app.route('/add_comment/<post_id>', methods=['POST'])
def add_comment(post_id):
    # Отримуємо дані коментаря з форми
    comment_data = {
        'comment_id': str(ObjectId()),  # Генеруємо унікальний ідентифікатор для коментаря
        'user_id': request.form.get('user_id'),
        'content': request.form.get('content'),
        'created_at': datetime.utcnow()
    }

    # Перевірка обов'язкових полів
    if not comment_data['user_id'] or not comment_data['content']:
        return jsonify({'error': 'User ID and content are required'}), 400

    # Додаємо коментар у пост
    result = posts_collection.update_one(
        {'post_id': post_id},
        {'$push': {'comments': comment_data}}
    )

    if result.matched_count == 0:
        return jsonify({'error': 'Post not found'}), 404

    return redirect(url_for('get_posts'))


@app.route('/view_comments/<post_id>', methods=['GET'])
def view_comments(post_id):
    # Отримуємо пост за його ID
    post = posts_collection.find_one({'post_id': post_id})
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    # Відображаємо коментарі у шаблоні
    return render_template('view_comments.html', post=post)


@app.route('/add_like/<post_id>', methods=['POST'])
def add_like(post_id):
    user_input = request.form.get('user_id')
    if not user_input:
        return jsonify({'error': 'User ID or name is required'}), 400

    # Пошук користувача за ObjectId або ім'ям
    try:
        user = users_collection.find_one({'_id': ObjectId(user_input)})
    except:
        user = users_collection.find_one({'name': user_input})

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Додаємо ім'я користувача до масиву лайків
    user_name = user['name']  # Отримуємо ім'я користувача
    posts_collection.update_one(
        {'post_id': post_id},
        {'$addToSet': {'likes': user_name}}  # Зберігаємо ім'я користувача
    )

    return redirect(url_for('get_posts'))
