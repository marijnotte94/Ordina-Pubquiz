from view import db, ma
import json

class Person(db.Model):
    """ users """
    __tablename__ = 'person'
    id = db.Column(db.Integer, primary_key=True)
    personname = db.Column(db.String(255))
    password = db.Column(db.String(255))


class PersonSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'personname')


class Team(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    teamname = db.Column(db.String(255))
    score = db.Column(db.Integer)


class TeamSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'teamname', 'score')


class Category(db.Model):
    """ category of question """
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class CategorySchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'name')


class Variant(db.Model):
    """ for some questions, multiple answers (variants) are correct """
    __tablename__ = 'variant'
    id = db.Column(db.Integer, primary_key=True)
    subanswer_id = db.Column(db.Integer, db.ForeignKey('subanswer.id'))
    answer = db.Column(db.String(255))
    isNumber = db.Column(db.Boolean)


class VariantSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'subanswer_id', 'answer', 'isNumber')


class SubAnswer(db.Model):
    """ question can have multiple subquestions, each subquestion has a subanswer """
    __tablename__ = 'subanswer'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    variants = db.relationship('Variant')


class SubAnswerSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'question_id', 'variants')
    variants = ma.Nested(VariantSchema(many=True))


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    createdby = db.relationship('Person')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    questioncategory = db.relationship('Category')
    question = db.Column(db.String(255))
    subanswers = db.relationship('SubAnswer')
    active = db.Column(db.Boolean)


class QuestionSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'person_id', 'category_id', 'question', 'active', 'subanswers', 'questioncategory', 'createdby')
    subanswers = ma.Nested(SubAnswerSchema(many=True))
    questioncategory = ma.Nested(CategorySchema)
    createdby = ma.Nested(PersonSchema)


class SubAnswerGiven(db.Model):
    """  """
    __tablename__ = 'subanswergiven'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable = False)
    corr_question = db.relationship('Question')
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable = False)
    answered_by = db.relationship('Team')
    corr_answer_id = db.Column(db.Integer, db.ForeignKey('subanswer.id'), nullable=False)
    corr_answer = db.relationship('SubAnswer')
    answer_given = db.Column(db.String(255))
    correct = db.Column(db.Boolean)
    confidence = db.Column(db.Float)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable = False)
    checkedby = db.relationship('Person')
    answer_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)


class SubAnswerGivenSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'question', 'team', 'answer_given', 'correct', 'person_id', 'checkedby', 'confidence', 'answer_image', 'image_width', 'image_height')
    checkedby = ma.Nested(PersonSchema)
    corr_question = ma.Nested(QuestionSchema)
    answered_by = ma.Nested(TeamSchema)


class Answersheet(db.Model):
    """ image of complete answersheet (handwritten) """
    __tablename__ = 'answersheet'
    id = db.Column(db.Integer, primary_key=True)
    answersheet_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)


class AnswerSheetQuestion(db.Model):
    """ answersheet corresponding to a question """
    __tablename__ = 'answersheetquestion'
    id = db.Column(db.Integer, primary_key=True)
    answersheet_id = db.Column(db.Integer, db.ForeignKey('answersheet.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))


class Word(db.Model):
    """ A word object, corresponding to words in a line. """
    __tablename__ = 'word'
    id = db.Column(db.Integer, primary_key=True)
    line_id = db.Column(db.Integer, db.ForeignKey('line.id'))
    word_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)


class Line(db.Model):
    """ A line object, corresponding to an answersheet line """
    __tablename__ = 'line'
    id = db.Column(db.Integer, primary_key=True)
    answersheet_id = db.Column(db.Integer, db.ForeignKey('answersheet.id'))
    line_image = db.Column(db.LargeBinary)
    image_width = db.Column(db.Integer)
    image_height = db.Column(db.Integer)

