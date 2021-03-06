from view import view, db
from flask import request, session, jsonify, url_for, flash
from view.models import Question, QuestionSchema, SubAnswer, Variant, Category, CategorySchema, Person, PersonSchema, AnswerGiven, AnswerGivenSchema


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


@view.route('/api/v1.0/category/<string:name>', methods=['GET'])
def get_category(name):
    categories_schema = CategorySchema()
    category = Category.query.filter_by(name=name).first()
    result = categories_schema.dump(category)
    return jsonify(result)


@view.route('/api/v1.0/persons', methods=['GET'])
def get_persons():
    persons_schema = PersonSchema(many=True)
    people = Person.query.all()
    result = persons_schema.dump(people)
    return jsonify(result)


@view.route('/api/v1.0/answers', methods=['GET'])
def get_answers():
    answers_schema = AnswerGivenSchema(many=True)
    allanswers = AnswerGiven.query.all()
    result = answers_schema.dump(allanswers)
    return jsonify(result)


@view.route('/api/v1.0/updatequestion', methods=['POST'])
def update_question():
    post = request.get_json()
    id = post.get('id')
    q = Question.query.filter_by(id=id).first()
    if str(post.get('questionnumber')).isdigit():
        questionnumber = int(post.get('questionnumber'))
        qtemp = Question.query.filter_by(questionnumber=questionnumber).first()
        if qtemp is None:
            q.questionnumber = questionnumber
        else:
            if qtemp.id != id:
                return 'De vraag kan niet worden aangepast. Er is al een vraag met dit nummer.'
            else:
                q.questionnumber = questionnumber
    else:
        return 'De vraag kan niet worden aangepast. Er is geen geldig vraagnummer ingevoerd'

    q.question = post.get('question')
    newsubanswers = post.get('subanswers')
    variants = []
    subanswers=[]
    for i in range(0, len(newsubanswers)):
        for j in range(0, len(newsubanswers[i]['variants'])):
            variant = Variant(answer=newsubanswers[i]['variants'][j]['answer'])
            variants.append(variant);
        subanswer = SubAnswer(variants=variants)
        subanswers.append(subanswer)
        variants = []
    q.subanswers = subanswers
    newcategory = post.get('category')
    category = Category.query.filter(Category.name == newcategory).first()
    if category is None:
        category = Category(name=newcategory)
    q.questioncategory = category
    db.session.commit()
    return 'OK'


@view.route('/api/v1.0/removequestion', methods=['POST'])
def remove_question():
    post = request.get_json()
    id = post.get('id')
    subanswers = SubAnswer.query.filter_by(question_id=id).all()
    try:
        for subanswer in subanswers:
            Variant.query.filter_by(subanswer_id=subanswer.id).delete()
        SubAnswer.query.filter_by(question_id=id).delete()
        Question.query.filter_by(id=id).delete()
        db.session.commit()
    except:
        return 'Vraag kan niet verwijderd worden. Er zijn nog antwoorden gekoppeld aan deze vraag'
    return 'OK'


@view.route('/api/v1.0/newquestion', methods=['POST'])
def add_question():
    post = request.get_json()
    newquestionnumber = post.get('questionnumber')
    if newquestionnumber.isdigit():
        newquestionnumber = int(newquestionnumber)
        qtemp = Question.query.filter_by(questionnumber=newquestionnumber).first()
        if qtemp is not None:
            return 'Fout: De vraag kan niet worden toegevoegd. Er is al een vraag met dit nummer.'
    else:
        return 'Fout: De vraag kan niet worden toegevoegd. Er is geen geldig vraagnummer ingevoerd'
    newquestion = post.get('question')
    newsubanswers = post.get('subanswers')
    subanswers = []
    variants = []
    for i in range(0, len(newsubanswers)):
        for j in range(0, len(newsubanswers[i]['variants'])):
            variant = Variant(answer=newsubanswers[i]['variants'][j]['answer'])
            variants.append(variant);
        subanswer = SubAnswer(variants=variants)
        subanswers.append(subanswer)
        variants = []
    newquestioncategory = post.get('category')
    category = Category.query.filter(Category.name == newquestioncategory).first()
    if category is None:
        category = Category(name=newquestioncategory)
    newquestionperson_id = session['userid']
    newquestionactive = post.get('active')
    q = Question(questionnumber=newquestionnumber, question=newquestion, questioncategory=category,
        person_id=newquestionperson_id, active=newquestionactive, subanswers=subanswers)
    db.session.add(q)
    db.session.commit()
    question_schema = QuestionSchema()
    result = question_schema.dump(q)
    return jsonify(result)


@view.route('/api/v1.0/resetquestionnumbers', methods=['POST'])
def resetnumbers():
    questions = Question.query.all()
    for question in questions:
        question.questionnumber = None
    db.session.commit()
    return 'OK'


@view.route('/api/v1.0/deleteallquestions', methods=['POST'])
def deletequestions():
    try:
        Variant.query.delete()
        db.engine.execute('alter sequence variant_id_seq RESTART with 1')
        SubAnswer.query.delete()
        db.engine.execute('alter sequence subanswer_id_seq RESTART with 1')
        Question.query.delete()
        db.engine.execute('alter sequence question_id_seq RESTART with 1')
        db.session.commit()
    except:
        return 'Vragen kunnen niet verwijderd worden. Er zijn nog antwoorden gekoppeld aan tenminste een vraag'
    return 'OK'


@view.route('/api/v1.0/removecategory', methods=['POST'])
def remove_category():
    post = request.get_json()
    id = post.get('id')
    try:
        Category.query.filter_by(id=id).delete()
        db.session.commit()
    except:
        return 'Categorie kan niet verwijderd worden. Er zijn nog vragen gekoppeld aan deze categorie'
    return 'OK'


