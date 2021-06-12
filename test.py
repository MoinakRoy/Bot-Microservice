import os
from typing import Text
import cv2
import json
import bottle
import spacy
import random
import secrets
import easyocr
import wikipedia
from wit import Wit
from bson import json_util
from pylab import rcParams
from pymongo import MongoClient
import matplotlib.pyplot as plt
from IPython.display import Image
from fuzzywuzzy import fuzz,process
from bson.json_util import dumps, loads
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, url_for
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser


app = Flask(__name__)

try:
    client = MongoClient('localhost', 27017)
    db = client['mongodb']
    faqcol = db['mongocol']

except:
    print("somthing went wrong in database connection!!")

UPLOAD_FOLDER = "C:\\New\\flask_testAPI\\picture"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def save_file(from_file):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(from_file.filename)
    file_fn = random_hex + f_ext
    file_path = os.path.join(app.root_path, 'picture', file_fn)
    from_file.save(file_path)
    return file_fn


@app.route("/get_data", methods=["GET"])
def get_seeds():
    all_seeds = list(faqcol.find({}))
    return json.dumps(all_seeds, default=json_util.default)

@app.route('/')
def index():
    return '''
         <form method="POST" action="/pdf_reader" enctype="multipart/form-data">
             <input type="text" name="username" required>
             <input type="file" name="user_upload">
             <input type="submit">
         </form>
    '''

@app.route('/image_read', methods = ['POST'])
def success():
    if request.method == "POST":
       #'user_upload' in request.files:

        user_upload = request.files['user_upload']
        file_upload = save_file(user_upload)
        faqcol.insert({'username': request.form.get('username'), 'photo_name': file_upload})


        rcParams['figure.figsize'] = 8, 16
        reader = easyocr.Reader(['en'])
        Image(f'picture/{file_upload}')
        output = reader.readtext(f'picture/{file_upload}')
        cord = output[-1][0]
        x_min, y_min = [int(min(idx)) for idx in zip(*cord)]
        x_max, y_max = [int(max(idx)) for idx in zip(*cord)]
        image = cv2.imread(f'picture/{file_upload}')
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
        plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        text = ''
        for result in output:
            text += result[1] + ''
        os.unlink(os.path.join(app.root_path,"picture", file_upload))
        return text

@app.route('/Spacy', methods = ['POST'])
def func_spcy_text():
    quest = request.json['user_quest']
    user_quest = quest
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(user_quest)
    st=""
    for ent in doc.ents:
        st+=ent.text
        st+=" "
        print(ent.text , ent.label_ , str(spacy.explain(ent.label_)),sep= " \t")  

    return st

'''
@app.route('/Spacy', methods = ['POST'])
def func_spcy_text():
    quest = request.json['user_quest']
    user_quest = quest
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(user_quest)
    
    for ent in doc.ents:
         return(f'{ent.text:{15}} {ent.start_char:{15}} {ent.end_char:{20}}  {ent.label_:{20}} {spacy.explain(ent.label_)} ')
'''
'''
    user_txt = ""
    client=Wit('NYQ2ZYOSKB3LVGXYDKLIDZAMZLKTCWPD')
    main_dict=client.message(user_txt)
    print(main_dict)
    ent_dict=main_dict['entities']
    keys=ent_dict.keys()
    li=[]
    st = ""
    for key in keys:
        pro_list=ent_dict[key]
        val=pro_list[0]['body']
        li.append(val)
    for i in li:
        st+=i
        st+=" "
    return st
    #values=filter_values(user_txt=txt,token=token)
    #print(values)
'''

@app.route("/fuzzy", methods=["POST"])
def storing_ques(data):
    quest = request.json['user_quest']
    user_quest = quest
    return user_quest
def get_matcher(question,container,limit=1):
    quest = request.json['user_quest']
    user_quest = quest
    result=process.extract(question,container,limit=limit)
    question=result[0][0]
    return question

def prede_ans(data,question):
    cont=data["FAQ"]
    print(question)
    for ct in cont:
        if ct['question']==question:
            print(ct['answer'])

@app.route("/answer", methods=["POST"])
def add_data():

    quest = request.json['user_quest']
    user_quest = quest

    if not quest:
        return jsonify({"Error":"Invalid Question"})
    else:

        try:
            
            def get_matcher(query, choice, limit=1):
                result = process.extract(query, choice, limit=limit)
                return result[0][0]
            
                           
            def prede_ans(question):
                print(question)
                for ct in key:

                    if ct['question']==question:
                        return ct['answer']
                

            Get_Answer = faqcol.find_one({"FAQ": {"$elemMatch": {"question": quest}}},{"FAQ.answer.$": 1, "FAQ.faqtype": "Returns", "FAQ._id": 1})
            answer = ""
            for i in Get_Answer["FAQ"]:
                answer = i['answer']
            if Get_Answer:
                return jsonify({"Answer": answer})
                # to create a new document to insert a new FQA
                #faqcol.insert({"title": "userfaq", "user_quest": [{"question": "quest"}]})
                #faqcol.update({"title": "userfaq"}, {"$push": {"user_quest": {"question": quest}}})


        except :
            lt=[]
            #print("Exception Mongo Query : ", e)
            with open('faq23.json') as input_json:
                json_data = json.load(input_json)
                key=json_data['FAQ']
                for t in key:
                    lt.append(t['question'])
              
                res = get_matcher(user_quest, lt)
                
                for an in key:
                    if an['question']==res:
                        return an['answer']
                return res
            #Default_Answer = wikipedia.summary(user_quest, sentences = 3)

        else:
            return jsonify({"ERROR":"Something Went Wrong!!"})


@app.route("/pdf_reader", methods=["POST"])
def pdf2text():
    user_upload = request.files['user_upload']
    file_upload = save_file(user_upload)
    faqcol.insert({'username': request.form.get('username'), 'photo_name': file_upload})

    output_string = StringIO()
    in_file = open(f'picture/{file_upload}', 'rb')
    parser = PDFParser(in_file)
    doc = PDFDocument(parser)
    rsrcmgr = PDFResourceManager()
    device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)

    text = output_string.getvalue()

    text = text.encode('utf-8')
    os.unlink(os.path.join(app.root_path, "picture", file_upload))
    return text

#file = open(f'{save_file_name}' + '.txt', 'wb')
#file.write(text)
#file.close()

#f = f'picture/{file_upload}'
#file = 'pree'
#pdf2text(f, file)



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