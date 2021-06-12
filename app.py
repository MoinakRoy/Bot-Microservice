from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
from bson import json_util
import random
import json


app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client['mongodb']
faqcol = db['mongocol']

@app.route("/get_data", methods=["GET"])
def get_seeds():
    all_seeds = list(faqcol.find({}))
    return json.dumps(all_seeds, default=json_util.default)

Default_Answer= "We have acknowledged your query, we will get back to you soon"
user_quest = "i want to explou sdasd ds"


@app.route("/answer", methods=["POST"])
def add_data():
    quest = request.json['user_quest']
    if not quest:
        return jsonify({"Error":"Invalid Question"})
    else:

        try:
            print("sdfdfdsf")
            Get_Answer = faqcol.find_one({"FAQ": {"$elemMatch": {"question": quest}}},
        {"FAQ.answer.$": 1, "FAQ.faqtype": "Returns", "FAQ._id": 1})
            answer = ""
            for i in Get_Answer["FAQ"]:
                answer = i['answer']
            if Get_Answer:
                return jsonify({"Answer": answer})
                # to create a new document to insert a new FQA
                #faqcol.insert({"title": "userfaq", "user_quest": [{"question": "quest"}]})
                #faqcol.update({"title": "userfaq"}, {"$push": {"user_quest": {"question": quest}}})



        except Exception as e:
            print("Exception Mongo Query : ", e)
            return jsonify({"Answer": Default_Answer})
    return jsonify({"ERROR":"Something Went Wrong!!"})

@app.route("/insert_data", methods=["POST"])
def insert_data():
        #Below code to Open Json file and deserialize object containing json document to python object
        with open('faq23.json') as input_json:
            json_data = json.load(input_json)
        # insert many if data contains list if not insert_one.
        if isinstance(json_data, list):
            print("List of documents availble in json")
            faqcol.insert_many(json_data)
        else :
            print("Single documents availble in json")
            faqcol.insert_one(json_data)


if __name__ == "__main__":
    app.run(debug=True)