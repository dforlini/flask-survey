from flask import Flask, request, render_template, redirect, flash, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from surveys import Survey, Question, satisfaction_survey, personality_quiz, surveys

app = Flask(__name__)
app.config['SECRET_KEY'] = "oh-so-secret"
#set to true to use debug tool
app.config['DEBUG_TB_ENABLED'] = False 
debug = DebugToolbarExtension(app)

responses = []

@app.route('/initialize_survey', methods=['POST'])
def initialize_survey():
    survey_name = request.form.get('survey_name')
    
    if survey_name not in surveys:
        flash("Invalid survey selected", "error")
        return redirect(url_for('show_survey_selection'))
    
    session['current_survey'] = survey_name
    session[f'{survey_name}_responses'] = []
    
    return redirect(url_for('show_question', survey_name=survey_name, qid=0))


@app.route('/')
def show_survey_selection():
   return render_template('select_survey.html', surveys=surveys)


@app.route('/start', methods=['POST'])
def start_survey():
    survey_name = request.form.get('survey_name')
    
    if survey_name not in surveys:
        flash("Invalid survey selected", "error")
        return redirect(url_for('show_survey_selection'))
    
    session['survey_started'] = True
    session[f'{survey_name}_responses'] = []
    session['current_survey'] = survey_name
    
    return redirect(url_for('show_question', survey_name=survey_name, qid=0))


@app.route('/questions/<int:qid>')
def show_question(qid):
    current_survey_key = session.get('current_survey')
    if not current_survey_key or current_survey_key not in surveys:
        flash("no surveys selected", "error")
        return redirect(url_for('show_survey_selection'))
    current_survey = surveys[current_survey_key]
    responses = session.get(f'{current_survey_key}_responses', [])
    
    if qid < 0 or qid >= len(current_survey.questions):
        flash("Question does not exist", "error")
        return redirect(url_for('show_survey_selection'))

    if len(responses) >= len(current_survey.questions):
        return redirect(url_for('survey_complete'))

    if qid != len(responses):
        flash("You are trying to access an invid question.", "error")
        return redirect(url_for('show_question', qid=len(responses)))

    question = current_survey.questions[qid]
    return render_template('questions.html', question_num=qid, question=question)


@app.route('/answer', methods=['POST'])
def handle_answer():
   current_survey_key = session.get('current_survey')
   responses_key = f'{current_survey_key}_responses'
   responses = session.get(responses_key, [])
   
   choice = request.form['choice']
   responses.append(choice)
   session[responses_key] = responses
   
   if len(responses) < len(surveys[current_survey_key].questions):
       return redirect(url_for('show_question', survey_name=current_survey_key, qid=len(responses)))
   else:
       return redirect(url_for('survey_complete'))

@app.route('/complete')
def survey_complete():
    session['survey_completed'] = True
    return render_template('complete.html')


@app.route('/reset')
def reset_survey():
    session.clear()
    flash('SURVEY HAS BEEN RESET')
    return redirect('/')