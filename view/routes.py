from view import view, db
from flask import Flask, jsonify, render_template, abort, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
import main
import json
import random
import string
import datetime
import app
import cv2
import numpy as np
from view.models import Team, TeamSchema, Question, QuestionSchema, Category, CategorySchema, Answersheet, User, \
    UserSchema
from werkzeug.utils import secure_filename
from collections import OrderedDict


@view.route('/')
@view.route('/index')
def index():
    return render_template('index.html')


@view.route('/questions')
def questions():
    return render_template('questions.html')


@view.route('/api/v1.0/teams', methods=['GET'])
def get_teams():
    teams_schema = TeamSchema(many=True)
    teams = Team.query.all()
    result = teams_schema.dump(teams)
    return jsonify(result)


@view.route('/api/v1.0/questions', methods=['GET'])
def get_questions():
    questions_schema = QuestionSchema(many=True)
    allquestions = Question.query.all()
    result = questions_schema.dump(allquestions)
    return jsonify(result)


@view.route('/api/v1.0/categories', methods=['GET'])
def get_categories():
    categories_schema = CategorySchema(many=True)
    allcategories = Category.query.all()
    result = categories_schema.dump(allcategories)
    return jsonify(result)


@view.route('/api/v1.0/users', methods=['GET'])
def get_users():
    users_schema = UserSchema(many=True)
    allusers = User.query.all()
    result = users_schema.dump(allusers)
    return jsonify(result)


@view.route('/api/v1.0/newquestion', methods=['POST'])
def add_question():
    post = request.get_json();
    newquestion = post.get('question')
    newquestioncorrect_answer = post.get('correct_answer')
    newquestioncategory_id = post.get('category_id')
    newquestionuser_id = post.get('user_id')
    newquestionactive = post.get('active')
    q = Question(question=newquestion, correct_answer=newquestioncorrect_answer, category_id=newquestioncategory_id,
                 user_id=newquestionuser_id, active=newquestionactive);
    db.session.add(q)
    db.session.commit()


@view.route('/api/v1.0/updatequestion', methods=['POST'])
def update_question():
    post = request.get_json();
    id = post.get('id')
    questionactive = post.get('active')
    q = Question.query.filter_by(id=id).first()
    q.active = questionactive
    db.session.commit()


@view.route('/run_program')
def run_program():
    # We wil use this url shortcut to start the program
    main.run_program()
    return line


@view.route('/answersheet/nuke', methods=['GET'])
def nuke_all_answersheets():
    Answersheet.query.delete()
    db.session.commit()
    db.engine.execute('alter sequence answersheet_id_seq RESTART with 1')
    return 'ok'


@view.route("/answersheet/save", methods=['GET', 'POST'])
def answersheet_save():
    # The image of a scan
    answer_image = app.save_answersheet()
    # convert the image to byte array so it can be saved in the database
    answer = answer_image.tostring()
    # create an Image object to store it in the database
    new_answersheet = Answersheet(answersheet_image=answer)
    # add the object to the database session
    db.session.add(new_answersheet)
    # commit the session so that the image is stored in the database
    db.session.commit()
    return "answersheets saved"


@view.route("/load_answersheet/<int:question_id>", methods=['GET', 'POST'])
def load_answersheet(question_id):
    answersheet = Answersheet.query.filter_by(id=question_id).first()
    if answersheet is None:
        return "answersheet with id " + str(question_id) + " does not exist in the database."
    image_data = answersheet.answersheet_image
    # I need to know the exact shape it had in order to load it from the database
    np_answersheet = np.fromstring(image_data, np.uint8).reshape(5848, 4139, 3)

    ret, png = cv2.imencode('.png', np_answersheet)
    response = make_response(png.tobytes())
    response.headers['Content-Type'] = 'image/png'
    return response


@view.route("/answersheet/load/<int:answersheet_id>", methods=['GET', 'POST'])
def answersheet_single(answersheet_id):
    return render_template("answersheet.html", answersheet_id=[answersheet_id])


@view.route("/answersheet/load", methods=['GET', 'POST'])
def answersheet_all():
    answersheets = Answersheet.query.all()
    ids = []
    for answersheet in answersheets:
        ids.append(int(answersheet.id))
    return render_template("answersheet.html", answersheet_id=ids)

