from flask import Flask, render_template, make_response, jsonify, request
from flask_restful import Resource, Api
from DataStatistics import DataStat as ds
import pandas as pd
import csv



# Initialize Flask

app = Flask(__name__)
api = Api(app)

PORT = 3200
DF = pd.DataFrame()
DATASETS = {}
COLUMNDATATYPES = {}
DATDICREF = {}  # Data Dictionary Reference
OBJDICREF = {}  # Object Dictionary Reference
NUMDICREF = {}  # Numeric Dictionary Reference
CATDICREF = {}  # Categorical Dictionary Reference
DATASETSNROOT = []
COLUMNNAMES = []
DATA = []

datasets = []
datasetFields = {}


class Dataset(Resource):

    # Endpoint to check a Query string validation
    @app.route("/qstr")
    def qs():
        if request.args:
            req = request.args
            res = {}
            for key, value in req.items():
                res[key] = value

            res = make_response(jsonify(res), 200)
            return res

        res = make_response(jsonify({"error": "No Query String"}), 404)
        return res

    # Endpoint to navigate a home page
    @app.route("/")
    def home():
        return render_template("/data.html")

    # Endpoint to Get a data page, and to Post and parse a dataset into HTML format
    @app.route("/<data>", methods=["GET", "POST"])
    def create(data):
        if request.method == "POST":  # should be capital here!!
            try:
                f = request.form["csvfile"]
                file_name = f
                dat = []
                with open(f) as file:
                    csvfile = csv.reader(file)
                    for row in csvfile:
                        dat.append(row)

                if len(dat) > 0:
                    datasets.clear()
                    DATASETSNROOT.clear()

                    key_memeber = {}
                    for i in range(len(dat)):
                        if i > 0:
                            dic = dict(zip(dat[0], dat[i]))
                            DATASETSNROOT.append(dic)
                            key_memeber['Row' + str(i)] = dic
                            DATASETS.update(key_memeber)

                df = pd.read_csv(file_name)
                global DF
                DF = df

                COLUMNDATATYPES.clear()
                DATDICREF.clear()
                OBJDICREF.clear()
                NUMDICREF.clear()
                CATDICREF.clear()

                for name, dtype in df.dtypes.iteritems():
                    COLUMNDATATYPES[name] = dtype

            
                # Return Dataset statistics
                DATDICREF.update(ds.get_data_stat(df, file_name))

                #Return Variables statistics
                for k, v in COLUMNDATATYPES.items():
                    
                    if (df[k].size - len(df[k].dropna().unique())) / df[k].size * 100 > 91:
                        CATDICREF.update(ds.get_cat_stat(df, k))
                    else:     
                        if v == 'object':
                            OBJDICREF.update(ds.get_obj_stat(df, k))  # Return column object statistics
                        elif v in ['int64', 'float64']:
                            NUMDICREF.update(ds.get_num_stat(df, k))  # Return column object statistics

                COLUMNNAMES.clear()  # To clear all previous columns of other dataset
                for col in list(df.columns):
                    COLUMNNAMES.append(col)

                data = pd.DataFrame(dat)
                data = data.to_html(header=False, index=False)
                return f"{data}"
            
            except ValueError:
                print('Invalid uploading file..')
        else:
            return render_template("data.html", data=data)

    # Endpoint to make a query from a Json structure or return error
    @app.route("/json/<collection>/<member>")
    def get_data(collection, member):
        print("getting the value of %s in the collection %s" % (member, collection))
        if collection in DATASETS:
            member = DATASETS[collection].get(member)
            if member:
                res = make_response(jsonify({"res": member}), 200)
                return res

            res = make_response(jsonify({"error": "A member not found"}), 404)
            return res

        res = make_response(jsonify({"error": "A collection not found"}), 404)
        return res

    # Endpoint to PUT a update a member value in a particular collection
    @app.route("/json/<collection>/<member>", methods=["PUT"])
    def put_col_mem(collection, member):
        req = request.get_json()

        if collection in DATASETS:
            if member:
                DATASETS[collection][member] = req["new"]
                res = make_response(jsonify({"res": DATASETS[collection]}), 200)
                return res

            res = make_response(jsonify({"error": "Memeber Not found"}), 404)
            return res

        res = make_response(jsonify({"error": "Collection Not found"}), 404)
        return res

    # Endpoint to DELETE a particular collection
    @app.route("/json/<collection>", methods=["DELETE"])
    def delete_col(collection):

        if collection in DATASETS:
            del DATASETS[collection]
            res = make_response(jsonify({"Success": "Collection is deleted"}), 200)
            return res

        res = make_response(jsonify({"error": "Collection not found"}), 404)
        return res

    @app.route("/json")
    def get_json():
        res = make_response(jsonify(DATASETS), 200)
        return res

    # Endpoint to GET data in a tabular format in the "getdata" HTML page
    @app.route("/datasets/getdata", methods=["GET"])
    def meta_data():
        return render_template("metadata.html", records=DATASETSNROOT, colnames=COLUMNNAMES)

    # Endpoint to POST a new row or a query from a Json structure or return error
    @app.route("/json/<collection>", methods=["POST"])
    def create_col(collection):
        req = request.get_json()

        if collection in DATASETS:
            res = make_response(jsonify({"error": "Collection already exists"}), 400)
            return res

        DATASETS.update({collection: req})

        res = make_response(jsonify({"message": "Collection created"}), 201)
        return res

    # Endpoint to GET data in a tabular format in the "description" HTML page
    @app.route("/datasets/description")
    def describe():
        return render_template("description.html", records=COLUMNDATATYPES, data_stat=DATDICREF, obj_stat=OBJDICREF,
                               num_stat=NUMDICREF, cat_stat=CATDICREF)
    
api.add_resource(Dataset, "/", "/json")

if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host='0.0.0.0', port=PORT)