from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# In-memory storage
users = {}
tasks = [
    {'id': 1, 'title': 'Task 1', 'description': 'Complete Task 1', 'reward': 10000, 'active': True, 'url': 'http://example.com/task1', 'duration': 30},
    {'id': 2, 'title': 'Task 2', 'description': 'Complete Task 2', 'reward': 20000, 'active': True, 'url': 'http://example.com/task2', 'duration': 60},
    # Add more tasks here
]
withdrawals = []
admin = {'phone_number': '083872543697', 'password': 'Kdsmedia@123'}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin/manage_users')
def manage_users():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    active_users = {phone: user for phone, user in users.items() if user.get('active', True)}
    inactive_users = {phone: user for phone, user in users.items() if not user.get('active', False)}
    return render_template('admin/manage_users.html', active_users=active_users, inactive_users=inactive_users)

@app.route('/admin/settings')
def settings():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/settings.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        if phone_number in users:
            session['user'] = phone_number
            return redirect(url_for('dashboard'))
        return 'User not found'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone_number = request.form['phone_number']
        if phone_number not in users:
            users[phone_number] = {'name': name, 'phone_number': phone_number, 'balance': 0, 'tasks_done': 0}
            return redirect(url_for('login'))
        return 'User already exists'
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_phone = session['user']
    user = users.get(user_phone, {})
    # Filter tasks that user has not completed yet
    tasks_to_display = [task for task in tasks if task['active'] and user_phone not in task.get('completed_users', [])]
    return render_template('dashboard.html', tasks=tasks_to_display)

@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
def task(task_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    user_phone = session['user']
    task = next((t for t in tasks if t['id'] == task_id), None)
    if request.method == 'POST':
        user = users.get(user_phone, {})
        if user['tasks_done'] < 10:
            user['balance'] += task['reward']
            user['tasks_done'] += 1
            # Add user to the task's completed list
            task.setdefault('completed_users', []).append(user_phone)
            return redirect(url_for('dashboard'))
        return 'You can only complete 10 tasks per day'
    return render_template('task.html', task=task)

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_phone = session['user']
    user = users.get(user_phone, {})
    return render_template('profile.html', user=user)

@app.route('/withdrawl', methods=['GET', 'POST'])
def withdrawl():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_phone = session['user']
    user = users.get(user_phone, {})
    if request.method == 'POST':
        amount = int(request.form['amount'])
        method = request.form['method']
        if method == 'bank':
            account_name = request.form['account_name']
            account_number = request.form['account_number']
            bank_name = request.form['bank_name']
            withdrawal = {
                'phone_number': user_phone,
                'amount': amount,
                'method': method,
                'status': 'Pending',
                'details': {'account_name': account_name, 'account_number': account_number, 'bank_name': bank_name}
            }
        else:
            withdrawal = {
                'phone_number': user_phone,
                'amount': amount,
                'method': method,
                'status': 'Pending',
                'details': {}
            }
        withdrawals.append(withdrawal)
        user['balance'] -= amount
        return redirect(url_for('profile'))
    return render_template('withdrawl.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == admin['phone_number'] and password == admin['password']:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        return 'Invalid credentials'
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    active_users = {phone: user for phone, user in users.items() if user.get('active', True)}
    inactive_users = {phone: user for phone, user in users.items() if not user.get('active', False)}
    return render_template('admin/dashboard.html', active_users=active_users, inactive_users=inactive_users)

@app.route('/admin/manage_user', methods=['POST'])
def manage_user():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    phone_number = request.form['phone_number']
    action = request.form['action']
    user = users.get(phone_number, {})
    if action == 'block':
        user['active'] = False
    elif action == 'unblock':
        user['active'] = True
    elif action == 'delete':
        users.pop(phone_number, None)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/transaksi')
def admin_transactions():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/transaksi.html', withdrawals=withdrawals)

@app.route('/admin/process_withdrawal', methods=['POST'])
def process_withdrawal():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    request_id = int(request.form['request_id'])
    action = request.form['action']
    withdrawal = withdrawals[request_id]
    if action == 'approve':
        withdrawal['status'] = 'Approved'
        user = users.get(withdrawal['phone_number'], {})
        user['balance'] -= withdrawal['amount']
    elif action == 'reject':
        withdrawal['status'] = 'Rejected'
    return redirect(url_for('admin_transactions'))

@app.route('/admin/add_task', methods=['POST'])
def add_task():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    title = request.form['title']
    description = request.form['description']
    url = request.form['url']
    reward = int(request.form['reward'])
    duration = int(request.form['duration'])
    task_id = len(tasks) + 1
    task = {
        'id': task_id,
        'title': title,
        'description': description,
        'url': url,
        'reward': reward,
        'duration': duration,
        'active': True
    }
    tasks.append(task)
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/manage_tasks', methods=['POST'])
def manage_tasks():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    task_id = int(request.form['task_id'])
    action = request.form['action']
    task = next((t for t in tasks if t['id'] == task_id), None)
    if action == 'activate':
        if task:
            task['active'] = True
    elif action == 'deactivate':
        if task:
            task['active'] = False
    elif action == 'edit':
        new_title = request.form.get('new_task_title')
        new_description = request.form.get('new_task_description')
        new_url = request.form.get('new_task_url')
        new_reward = request.form.get('new_task_reward')
        new_duration = request.form.get('new_task_duration')
        if task:
            if new_title:
                task['title'] = new_title
            if new_description:
                task['description'] = new_description
            if new_url:
                task['url'] = new_url
            if new_reward:
                task['reward'] = int(new_reward)
            if new_duration:
                task['duration'] = int(new_duration)
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
