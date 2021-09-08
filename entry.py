from flask import Flask,request
import os
import mysql.connector
from werkzeug.utils import  secure_filename
from flask_cors import CORS,cross_origin
import time
app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3006"}})

# base_path = os.path.abspath(os.path.dirname(__file__))
# print(base_path)
# app.config['UPLOAD_FOLDER'] = os.path.join(base_path,base_path+'\\Uploads')
# upload_path = os.path.join(base_path, app.config['UPLOAD_FOLDER'])

# @app.route('/')
# def hello_world():
#    return ("Hello World")
#
# @app.route('/connect')
# def connect_to_server():
#    mydb = mysql.connector.connect(
#       host="9.46.64.176",
#       user="mysql",
#       password="password"
#    )
#    print(mydb)
#    return "success"
#
# @app.route('/SQLMigration',methods=['POST'])
# def sample_post_request():
#    print("Received Source Name : "+request.json['source']+"  Received File Location : "+request.json['fileLocation'])
#    return "Success"
#
# @app.route('/recvd',methods=['POST'])
# def copy_file_to_server():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
#    return 'file uploaded successfully'
#
#
# def dcw_migration(data_source, file_name):
#    data_source = data_source
#    file_name = file_name
#    if data_source == 'DB2':
#       cmd = "db_harmony_profiler.sh convert 6 {0}".format(file_name)
#       result = subprocess.check_output(cmd, shell=True)
#    else:
#       print("Unsupported data_source {0} is provided".format(data_source))
#    return result
#
#
# @app.route('/SQLMigration', methods=['POST'])
# def SQLMigration():
#    #We will copy and create file on the destination
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
#
#    #Process destination file
#    output = dcw_migration('DB2', '/mnt/clientdir/clienthome/db2inst1/COREDW_nzschema.sql')
#    if output.find('SUCCESS') != -1:
#       return ("SQL migration completed")
#    else:
#       return ("SQL migration failed")
#
# def dcw_migration(data_source, file_name):
#     data_source = data_source
#     file_name = file_name
#     if data_source == 'DB2WH':
#         cmd = "db_harmony_profiler.sh convert 6 {0}".format(file_name)
#         result = subprocess.check_output(cmd, shell=True)
#     else:
#         print("Unsupported data_source {0} is provided".format(data_source))
#     return result

@app.route('/SQLMigration', methods=['POST'])
@cross_origin(origin='localhost')
def SQLMigration():
    # f = request.files['file']
    # data = f.save(upload_path,secure_filename(f.filename))
    # data_source = request.form['data_source']
    time.sleep(2)
    return "success"

@app.route('/DATAMigration', methods=['POST'])
@cross_origin(origin='localhost')
def data_migration():
    # f = request.files['file']
    # data = f.save(upload_path,secure_filename(f.filename))
    # data_source = request.form['data_source']
    time.sleep(2)
    return "success"

@app.route('/QUERYExecution', methods=['POST'])
@cross_origin(origin='localhost')
def query_migration():
    # f = request.files['file']
    # data = f.save(upload_path,secure_filename(f.filename))
    # data_source = request.form['data_source']
    time.sleep(2)
    return "success"

@app.route('/PerfEngine', methods=['GET'])
@cross_origin(origin='localhost')
def perrf_engine():
    # f = request.files['file']
    # data = f.save(upload_path,secure_filename(f.filename))
    # data_source = request.form['data_source']
    return "success"

if __name__ == '__main__':
   app.run()