from asyncio.windows_events import NULL
from sqlite3 import Cursor
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
from datetime import datetime





app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'
cursor = db_conn.cursor()

@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route("/portfolio", methods=['GET', 'POST'])
def portfolio():
    return render_template('portfolio.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    salary_rate = request.form['salary_rate']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, NULL)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, salary_rate))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

@app.route('/directory', methods =['GET', 'POST'])
def directory():
    cursor.execute("SELECT * FROM employee")
    directoryData = cursor.fetchall()
    print(directoryData)
    return render_template('directory.html', data = directoryData, bucket=bucket)

@app.route('/editProfile', methods =['GET', 'POST'])
def editProfile():
    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        cursor.execute("SELECT * FROM employee WHERE emp_id="+data)
        directoryData = cursor.fetchone()
        print(directoryData)
        return render_template('editProfile.html', data = directoryData)

@app.route('/profile', methods =['GET', 'POST'])
def profile():
    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        cursor.execute("SELECT * FROM employee WHERE emp_id="+data)
        directoryData = cursor.fetchone()
        cursor.execute("SELECT * FROM performanceNote WHERE emp_id="+data)
        performanceData = cursor.fetchall()
        print(directoryData)
        print(performanceData)
        return render_template('profile.html', data = directoryData, bucket=bucket, performance = performanceData)

@app.route("/saveProfile", methods=['POST'])
def saveProfile():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    salary_rate = request.form['salary_rate']
    emp_image_file = request.files['emp_image_file']

    update_sql = "UPDATE employee SET first_name = %s, last_name = %s, pri_skill = %s, location = %s, salary_rate = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(update_sql, (first_name,last_name,pri_skill,location,salary_rate,emp_id))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.execute("SELECT * FROM employee WHERE emp_id="+emp_id)
        directoryData = cursor.fetchone()

    print("all modification done...")
    return render_template('profile.html', data = directoryData)

@app.route('/deleteProfile', methods =['GET', 'POST'])
def deleteProfile():
    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        cursor.execute("DELETE FROM employee WHERE emp_id="+data)
        return render_template('deletedProfile.html', data = data)

@app.route('/performanceAdd', methods =['GET', 'POST'])
def performanceAdd():
    today = datetime.now()
    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        return render_template('performanceAdd.html', data = data)

@app.route('/performanceSave', methods =['GET', 'POST'])
def performanceSave():
    today = datetime.now()
    todayDate = today.strftime("%Y-%m-%d")
    idDate = today.strftime("%y%m%d%H%M%S")
    if request.method == 'POST':
        emp_id = request.form["emp_id"]
        note = request.form["note"]
        date = todayDate
        id= str("PN" + idDate)
        print(id)
        print(date)
        print(note)
        print(emp_id)
        update_sql = "INSERT INTO performanceNote VALUES (%s, %s, %s, %s)"

        cursor.execute(update_sql, (id,date,note,emp_id))
        db_conn.commit()

        return render_template('performanceSaved.html' )
      

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
    