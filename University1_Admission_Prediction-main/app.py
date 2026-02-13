from flask import Flask, render_template, request, redirect, url_for, session
from flask_cors import CORS, cross_origin
import pickle
from sklearn.preprocessing import StandardScaler
import numpy as np
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# Simulated user database
users = {}

# Decorator to enforce login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Redirect root to login
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', message="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template('register.html', message="User already exists")
        users[username] = password
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'])

@app.route('/predict', methods=['GET', 'POST'])
@cross_origin()
@login_required
def predict():
    if request.method == 'POST':
        try:
            gre_score = float(request.form['gre_score'])
            toefl_score = float(request.form['toefl_score'])
            university_rating = float(request.form['university_rating'])
            sop = float(request.form['sop'])
            lor = float(request.form['lor'])
            cgpa = float(request.form['cgpa'])
            research = 1 if request.form['research'] == 'yes' else 0

            scaler = pickle.load(open("scaling_model.pkl", "rb"))
            predict_input = scaler.transform([[gre_score, toefl_score, university_rating, sop, lor, cgpa, research]])
            model = pickle.load(open("ridge_regression_model.pkl", "rb"))
            prediction = model.predict(predict_input)

            percent = round(prediction[0] * 100, 2)

            # Dummy college data based on chance tiers
            college_data = {}
            if percent >= 90:
                college_data = {
                    'name': 'Massachusetts Institute of Technology (MIT)',
                    'details': 'Top-ranked university with a strong focus on research and innovation.The Massachusetts Institute of Technology (MIT) is a private research university in Cambridge, Massachusetts, United States.',
                    'image': 'https://geekerhertz.com/images/609e3b7855689.jpg'
                }
            elif percent >= 75:
                college_data = {
                    'name': 'University of California, Berkeley',
                    'details': 'Prestigious public research university with excellent graduate programs.The University of California, Berkeley (UC Berkeley, Berkeley, Cal, or California), is a public land-grant research university in Berkeley, California, United States. ',
                    'image': 'https://www.greatcollegedeals.net/wp-content/uploads/2015/11/University-of-California-at-Berkeley.jpg'
                }
            elif percent >= 60:
                college_data = {
                    'name': 'University of Wisconsin–Madison',
                    'details': 'Highly respected for engineering and data science fields.he University of Wisconsin–Madison (University of Wisconsin, Wisconsin, UW, UW–Madison, or simply Madison) is a public land-grant research university in Madison, Wisconsin, United States. It was founded in 1848 when Wisconsin achieved statehood and is the flagship campus of the University of Wisconsin System. The 933-acre (378 ha) main campus is located on the shores of Lake Mendota; the university also owns and operates a 1,200-acre (486 ha) arboretum 4 miles (6.4 km) south of the main campus.',
                    'image': 'https://smapse.com/storage/2018/11/bascomhall.jpg'
                }
            else:
                college_data = {
                    'name': 'San Jose State University',
                    'details': 'Good university with accessible admissions and solid STEM programs.San José State University (San Jose State or SJSU) is a public research university in San Jose, California. Established in 1857, SJSU is the oldest public university on the West Coast and the founding campus of the California State University (CSU) system.The university, alongside the University of California, Los Angeles has academic origins in the historic normal school known as the California State Normal School.',
                    'image': 'https://images.shiksha.com/mediadata/images/1533813832phpeWuPgT_g.jpg'
                }

            return render_template('results.html', prediction=percent, college=college_data)

        except Exception as e:
            print('Prediction Error:', e)
            return 'An error occurred during prediction.'
    return render_template('index.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
