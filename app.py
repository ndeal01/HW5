from flask import Flask
from flask import render_template, redirect, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import pymysql
#import secrets
import os

dbuser = os.environ.get('DBUSER')
dbpass = os.environ.get('DBPASS')
dbhost = os.environ.get('DBHOST')
dbname = os.environ.get('DBNAME')

#conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(secrets.dbuser, secrets.dbpass, secrets.dbhost, secrets.dbname)
conn = "mysql+pymysql://{0}:{1}@{2}/{3}".format(dbuser, dbpass, dbhost, dbname)

app = Flask(__name__)
app.config['SECRET_KEY']='SuperSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = conn
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

db = SQLAlchemy(app)

class ndeal_cpu(db.Model):
    cpu_id = db.Column(db.Integer, primary_key=True)
    cpu_name = db.Column(db.String(255))
    cores = db.Column(db.Integer)
    clock = db.Column(db.Float)

    def __repr__(self):
        return "id: {0} | cpu name: {1} | cores: {2} | clock: {3}".format(self.id, self.cpu_name, self.cores, self.clock)

class CPUform(FlaskForm):
    cpu_id = IntegerField('CPU ID:')
    cpu_name = StringField('cpu name:', validators=[DataRequired()])
    cores = StringField('cores:', validators=[DataRequired()])
    clock = StringField('clock:', validators=[DataRequired()])


@app.route('/')
def index():
    all_cpus = ndeal_cpu.query.all()
    return render_template('index.html', cpu=all_cpus, pageTitle='AMD CPUs')

@app.route('/add_cpu', methods=['GET', 'POST'])
def add_cpu():
    form = CPUform()
    if form.validate_on_submit():
        cpu = ndeal_cpu(cpu_name=form.cpu_name.data, cores=form.cores.data, clock=form.clock.data)
        db.session.add(cpu)
        db.session.commit()
        return redirect('/')

    return render_template('add_cpu.html', form=form, pageTitle='Add A New CPU')

@app.route('/cpu/<int:cpu_id>/delete', methods=['POST'])
def delete_cpu(cpu_id):
    if request.method == 'POST': #if it's a POST request, delete the friend from the database
        cpu = ndeal_cpu.query.get_or_404(cpu_id)
        db.session.delete(cpu)
        db.session.commit()
        flash('CPU was successfully deleted!')
        return redirect("/")
    else: #if it's a GET request, send them to the home page
        return redirect("/")

@app.route('/cpu/<int:cpu_id>', methods=['GET','POST'])
def cpu(cpu_id):
    cpu = ndeal_cpu.query.get_or_404(cpu_id)
    return render_template('cpu.html', form=cpu, pageTitle='CPU Details')

@app.route('/cpu/<int:cpu_id>/update', methods=['GET','POST'])
def update_cpu(cpu_id):
    cpu = ndeal_cpu.query.get_or_404(cpu_id)
    form = CPUform()
    if form.validate_on_submit():
        cpu.cpu_name = form.cpu_name.data
        cpu.cores = form.cores.data
        cpu.clock = form.clock.data
        db.session.commit()
        flash('Your CPU has been updated.')
        return redirect("/")
    #elif request.method == 'GET':
    form.cpu_name.data = cpu.cpu_name
    form.cores.data = cpu.cores
    form.clock.data = cpu.clock
    return render_template('update_cpu.html', form=form, pageTitle='Update CPU',
                            legend="Update A CPU")
