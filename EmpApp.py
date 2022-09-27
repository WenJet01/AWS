from sqlite3 import Cursor
from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *


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
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
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
    return render_template('directory.html', data = directoryData)

@app.route('/editProfile', methods =['GET', 'POST'])
def editProfile():
    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        cursor.execute("SELECT * FROM employee WHERE emp_id="+data)
        directoryData = cursor.fetchone()
        print(directoryData)
        return render_template('editProfile.html', data = directoryData)

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
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
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
        cursor.execute("SELECT * FROM employee")
        directoryData = cursor.fetchall()

    print("all modification done...")
    
    
    return render_template('directory.html', data = directoryData)
      
@app.route('/important1', methods =['GET', 'POST'])
def important1():
    cursor.execute("SELECT * FROM employee")
    directoryData = cursor.fetchall()
    print(directoryData)
    return render_template('important1.html', data = directoryData)

@app.route('/important2', methods =['GET', 'POST'])
def important2():
    noFile = ""
    if request.method == 'POST':
        data = request.form["input"]
        print(data)

        cursor.execute("SELECT * FROM employee WHERE emp_id="+data)
        directoryData = cursor.fetchone()
        print(directoryData)

        try:

            cursor.execute("SELECT * FROM important WHERE emp_id="+data)
            directoryData2 = cursor.fetchall()
            print(directoryData2)


            if cursor.rowcount == 0:                
                noFile = " 0 File Uploaded. "

        except Exception as e:
            
            return str(e)
       
        return render_template('important2.html', data = directoryData , data2 = directoryData2, bucket = custombucket, noFile = noFile)



@app.route('/uploadfile', methods =['GET', 'POST'])
def uploadfile():
    emp_id = request.form['emp_id']
    emp_important_file = request.files['emp_important_file']
    important_id = "important_file_emp-id-" + str(emp_id) + "-" + str(emp_important_file.filename)

    insert_sql = "INSERT INTO important VALUES (%s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (important_id, emp_id))
        db_conn.commit()

        # Uplaod image file in S3 #
        emp_important_file_name_in_s3 = "important_file_emp-id-" + str(emp_id) + "-" + str(emp_important_file.filename)
        s3 = boto3.resource('s3')

        try:
            s3.Bucket(custombucket).put_object(Key=emp_important_file_name_in_s3, Body=emp_important_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_important_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.execute("SELECT * FROM employee")
        directoryData = cursor.fetchall()

    print("all modification done...")

    return render_template('success.html', data = directoryData)

@app.route('/leave1', methods =['GET', 'POST'])
def leave1():

    cursor.execute("SELECT * FROM appLeave WHERE status='pending'")
    directoryData = cursor.fetchall()
    print(directoryData)

    cursor.execute("SELECT * FROM appLeave WHERE status='accept'")
    directoryData2 = cursor.fetchall()
    print(directoryData2)

    cursor.execute("SELECT * FROM appLeave WHERE status='reject'")
    directoryData3 = cursor.fetchall()
    print(directoryData3)


    return render_template('leave1.html', data = directoryData, data2 = directoryData2, data3 = directoryData3)


@app.route('/leave2', methods =['GET', 'POST'])
def leave2():

    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        cursor.execute("SELECT * FROM appLeave WHERE appLeave_id='"+data+"'")
        directoryData = cursor.fetchone()
        print(directoryData)

        return render_template('leave2.html', data = directoryData)

@app.route('/leave3', methods =['GET', 'POST'])
def leave3():

    if request.method == 'POST':
        data = request.form["input"]
        print(data)
        cursor.execute("SELECT * FROM appLeave WHERE appLeave_id='"+data+"'")
        directoryData = cursor.fetchone()
        print(directoryData)

        return render_template('leave3.html', data = directoryData)


@app.route("/applyLeave", methods =['GET', 'POST'])
def applyLeave():
    appLeave_id = request.form["appLeave_id"]
    accept = "accept"

    update_sql = "UPDATE appLeave SET status = %s WHERE appLeave_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (accept,appLeave_id))
        db_conn.commit()
        
    finally:
        cursor.execute("SELECT * FROM appLeave")
        directoryData = cursor.fetchall()
    
    return render_template('success.html', data = directoryData)

@app.route("/rejectLeave", methods =['GET', 'POST'])
def rejectLeave():
    appLeave_id = request.form["appLeave_id"]
    reject = "reject"

    update_sql = "UPDATE appLeave SET status = %s WHERE appLeave_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (reject,appLeave_id))
        db_conn.commit()
        
    finally:
        cursor.execute("SELECT * FROM appLeave")
        directoryData = cursor.fetchall()
    
    return render_template('success.html', data = directoryData)


@app.route('/training1', methods =['GET', 'POST'])
def training1():
    cursor.execute("SELECT * FROM training")
    directoryData = cursor.fetchall()
    print(directoryData)

    cursor.execute("SELECT * FROM employee")
    directoryData2 = cursor.fetchall()
    print(directoryData2)

    return render_template('training1.html', data = directoryData, data2 = directoryData2)


@app.route('/training2', methods =['GET', 'POST'])
def training2():
    training_id = request.form["input"]
    cursor.execute("SELECT * FROM employee WHERE training_id IS NULL")
    directoryData = cursor.fetchall()
    print(directoryData)

    cursor.execute("SELECT * FROM training WHERE training_id='"+training_id+"'")
    directoryData2 = cursor.fetchone()
    print(directoryData2)

    return render_template('training2.html', data = directoryData, data2 = directoryData2)


@app.route("/joinTraining", methods =['GET', 'POST'])
def joinTraining():
    training_id = request.form["training_id"]
    emp_id = request.form["input"]

    update_sql = "UPDATE employee SET training_id = %s WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (training_id,emp_id))
        db_conn.commit()
        
    finally:
        cursor.execute("SELECT * FROM training")
        directoryData = cursor.fetchall()
    
    return render_template('success.html', data = directoryData)


@app.route("/exitTraining", methods =['GET', 'POST'])
def exitTraining():
    emp_id = request.form["input"]

    update_sql = "UPDATE employee SET training_id = NULL WHERE emp_id = %s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(update_sql, (emp_id))
        db_conn.commit()
        
    finally:
        cursor.execute("SELECT * FROM training")
        directoryData = cursor.fetchall()
    
    return render_template('success.html', data = directoryData)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)