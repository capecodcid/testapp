from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from datetime import datetime
import pickle, os
import pandas as pd
import numpy as np
import random

app = Flask(__name__)
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test2.db'
db = SQLAlchemy(app)

df = pd.read_pickle(os.path.join(app.root_path, 'static/data/embeddings.pkl'))

def dist_to_query(query, target):
	return np.linalg.norm(query-target)

def find_n_closest(q_idx, df, n):
	query = df.loc[df.idx == q_idx]['embedding'].to_numpy()[0]
	df['dist'] = df.apply(lambda row: dist_to_query(query, row['embedding']), axis = 1)
	return df.sort_values(by=['dist']).iloc[1:1+n]['idx'].to_list()

def find_n_random(df, n):
	return random.sample(df.idx.to_list(), n)

@app.route('/', methods=['POST','GET'])
def index():
	if request.method == 'POST':
		label_option = 1 if (request.form['options'] == 'right') else 0
		new_label = Label(user=6, option=label_option, gt=1)
		try:
			db.session.add(new_label)
			db.session.commit()
			return redirect('/')
		except:
			return 'There was an issue saving your label'
	else:
		qidx = random.randrange(1000)
		gt = random.randrange(1) 
		n = 3
		filename = f"imgs/{qidx}.png"
		qimg = url_for('static', filename=filename)
		result_inds = find_n_closest(qidx, df, n)
		random_inds = find_n_random(df, n)
		result_urls = [url_for('static', filename=f"imgs/{idx}.png") for idx in result_inds]
		random_urls = [url_for('static', filename=f"imgs/{idx}.png") for idx in random_inds]
		
		return render_template('test2.html', qimg=qimg, images=zip(result_urls, random_urls))

@app.route('/data')
def show_data():
	labels = Label.query.order_by(Label.date_created).all()
	return render_template('data.html', labels=labels)


# 0 = LEFT, 1 = RIGT
class Label(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.Integer, nullable=False)
	option = db.Column(db.Integer, nullable=False)
	gt = db.Column(db.Integer, nullable=False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<Label %r>' % self.id

# @app.route('/', methods=['POST','GET'])
# def index():
# 	if request.method == 'POST':
# 		task_content = request.form['content']
# 		new_task = Todo(content=task_content)
# 		try:
# 			db.session.add(new_task)
# 			db.session.commit()
# 			return redirect('/')
# 		except:
# 		 	return 'There was an issue adding your task'
# 	else:
# 		tasks = Todo.query.order_by(Todo.date_created).all()
# 		return render_template('index.html', tasks=tasks)


# @app.route('/delete/<int:id>')
# def delete(id):
# 	task_to_delete = Todo.query.get_or_404(id)

# 	try:
# 		db.session.delete(task_to_delete)
# 		db.session.commit()
# 		return redirect('/')

# 	except:
# 		return 'There was a problem deleting your task'		

# @app.route('/update/<int:id>', methods=['POST','GET'])
# def update(id):
# 	task = Todo.query.get_or_404(id)
# 	if request.method == 'POST':
# 		task.content = request.form['content']
# 		try:
# 			db.session.commit()
# 			return redirect('/')
# 		except:
# 			return 'There was an issue with your update.'

# 	else:
# 		return render_template('update.html',task=task)

if __name__ == "__main__":
	app.run(debug=True)