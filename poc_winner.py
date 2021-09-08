import os, subprocess, datetime, scandir, MySQLdb, glob
from werkzeug.utils import secure_filename
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
from flask import Flask, request, jsonify  # import main Flask class and request object
from flask_cors import CORS, cross_origin  # import to resolve CORS

app = Flask(__name__)  # create the Flask app

CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "http://9.46.64.176:32653"}})

base_path = os.path.abspath(os.path.dirname(__file__))
app.config["UPLOAD_FOLDER"] = os.path.join(base_path, base_path + "/Uploads/SqlMigration/")
upload_path = os.path.join(base_path, app.config["UPLOAD_FOLDER"]) # form upload path

def dcw_migration(data_source, file_name):
    '''Function to evaluate SQL compatibility'''
    data_source = data_source
    file_name = file_name
    if data_source == "DB2":
        cmd = "db_harmony_profiler.sh evaluate 6 {0} overallreport".format(file_name)
        result = subprocess.check_output(cmd, shell=True)
    else:
        print("Unsupported data_source {0} is provided".format(data_source))
    return result

# App for SQL migration
@app.route("/SQLMigration", methods=["POST"])
@cross_origin(origin="http://9.46.64.176")
def SQLMigration():
    for f in request.files.getlist("file"):
        f.save(os.path.join(upload_path, secure_filename(f.filename))) # save multiple files as a multipart form data
    data_source = request.form["data_source"]
    output = dcw_migration(data_source, upload_path)
    if output.find("SUCCESS") != -1:
        os.chdir(upload_path)
        report_file = glob.glob("Overall_*.html") # search for report HTML file
        report_file.sort()
        with open(report_file[-1]) as f:
            page = f.read()
            parsed_html = BeautifulSoup(page)
            desired_text = parsed_html.body.find(
                "div", attrs={"class": "overall_summary"}
            ).text.split()
            total_sql = desired_text[4]
            converted_sql = desired_text[1].replace("Summary", "")
            compatibility = desired_text[6]
            data = {
                "Total statements in SQL file": total_sql,
                "SQL statements converted": converted_sql,
                "Compatibility%": compatibility,
            }
        response = jsonify(data)
        return response
    else:
        return jsonify("SQL migration failed")

def data_migration(shost, sdb, table):
    '''Function to perform data migration'''
    cmd = "db_migrate -suser admin -tuser bluadmin -spassword password -tpassword bluadmin -sdb {0} -tdb bludb63 -shost {1} -CreateTargetTable yes -format binary -skip_numeric_check -TruncateTargetTable yes -t {2} -tschema hackathon".format(sdb, shost, table)
    result = subprocess.check_output(cmd, shell=True)
    return result

# App for Data migration
@app.route('/DATAMigration', methods=['POST'])
@cross_origin(origin='http://9.46.64.176')
def DATAMigration():
    source_host = request.json['shost']
    source_db = request.json['sdb']
    table_name = request.json['table']
    output = data_migration(source_host, source_db, table_name)
    if output.find('Number of tables with mismatched data') == -1:
        assert output.find('confirmed: source/target table row count') != -1
        for item in output.split("\n"):
            if 'Total # of tables processed' in item:
                total_tables = item.split(':')[-1]
            if 'Total # of records unloaded' in item:
                total_records = item.split(':')[-1]
            if '# of seconds to unload/load the records' in item:
                total_secs = item.split(':')[-1]
        data = {
            "Message":"Data migration is successful",
            "Total tables processed":total_tables,
            "Total records migrated":total_records,
            "Time (in secs) to load the records": total_secs
        }
        response = jsonify(data)
        return response
    else:
        return jsonify("Data migration failed!")

base_path = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(base_path,base_path+'/Uploads/Workload/')
upload_path = os.path.join(base_path, app.config['UPLOAD_FOLDER'])
db_host,user,passwd,db,port = ("9.46.64.176","root","password","mysql",31290) # mysql connection parameters

# App for workload execution
@app.route('/WORKLOADExecution', methods=['POST'])
@cross_origin(origin='http://9.46.64.176')
def WORKLOADExecution():
    for f in request.files.getlist("file"):
        f.save(os.path.join(upload_path, secure_filename(f.filename)))
    file_names = scandir.scandir(upload_path) # get all file names from upload path
    db_type = request.form['database = 'NETEZZA'
    host = request.form['host']
    sql_files_list = []
    conn = MySQLdb.connect(db_host,user,passwd,db,port)
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    sql = "select max(session_id) from stats_file_level"
    cursor.execute(sql)
    result_id = cursor.fetchall()
    session_id = result_id[0]['max(session_id)']
    session_id += 1 # session id for each workload session
    for sql_file in file_names:
        if sql_file.name.endswith(".sql") and sql_file.is_file():
            sql_files_list.append(sql_file.name)
            start_time = datetime.datetime.now()
            sql = "select distinct(fileid) from stats_file_level where filename like '{}'".format(sql_file.name)
            cursor.execute(sql)
            result_id = cursor.fetchall()
            if result_id:
                file_id = result_id[0]['fileid'] # use file id already mapped to sql
            else:
                sql = "select max(fileid) from stats_file_level"
                cursor.execute(sql)
                result_id = cursor.fetchall()
                file_id = result_id[0]['max(fileid)']
                file_id += 1 # generate file id for new sql
            if db_type == 'NETEZZA':
                cmd = "nzsql -h {0} -d coredw -u admin -W password -f {1}/{2}".format(host, upload_path, sql_file.name)
            elif db_type == 'DB2':
                cmd = "dbsql -h {0} -d bludb -u bluadmin -W bluadmin -f {1}/{2}".format(host, upload_path, sql_file.name)
            result = subprocess.check_output(cmd, shell=True)
            end_time = datetime.datetime.now()
            time_diff = end_time - start_time
            time_diff_in_s = time_diff.seconds # execution time in seconds
            sql = "insert into stats_file_level(session_id,fileid,starttime,endtime,exectime,dbtype,filename) values ({},{},'{}','{}',{},'{}','{}')".format(session_id, file_id, start_time, end_time, time_diff_in_s, db_type, sql_file.name)
            cursor.execute(sql)
            conn.commit()
    sql = 'select sum(exectime) from stats_file_level where filename in ({}) and session_id = {}'.format(','.join(['%s'] * len(sql_files_list)), session_id)
    cursor.execute(sql, sql_files_list)
    result = cursor.fetchall()
    total_time_diff_in_s = result[0]['sum(exectime)'] # total execution time for a particular session
    conn.close()
    data = {
        "Message":"Workload execution completed",
        "Duration of workload execution":"{0} seconds".format(total_time_diff_in_s)
    }
    response = jsonify(data)
    return response

app.run(debug=True, host='0.0.0.0', port=5000)