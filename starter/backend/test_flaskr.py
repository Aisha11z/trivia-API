import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('postgres:postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.question_id=0
        self.new_question = {
            'question': 'How far away is the sun?',
            'answer': '93 million miles away',
            'category': 1,
            'difficulty': 2
        }
        self.quiz_data={
            'previous_questions': [20, 21, 22],
            'quiz_category': {'id': 1, 'type': 'Science'}
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsInstance(data['categories'], dict)

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertLessEqual(len(data['questions']), 10)
        self.assertIsInstance(data['total_questions'], int)
        self.assertIsInstance(data['categories'], dict)
    
    def test_add_question(self):
        res = self.client().post('/questions',
        data=json.dumps(self.new_question),
        content_type='application/json')
        data = json.loads(res.data)
        self.question_id=data['created']
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(data['question'])

    def test_add_question_fail(self):
        res = self.client().post('/questions',
        data=json.dumps({}),
        content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'unprocessable')

    def test_delete_question(self):  
        test_question = Question(question='why this question', answer='to test the delete question operation',
        difficulty=1, category=1)
        test_question.insert()
        test_question_id = test_question.id     
        res = self.client().delete('/questions/{}'.format(test_question_id))
        data = json.loads(res.data)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], test_question_id)

    def test_delete_question_fail(self):
        res = self.client().delete('/questions/40')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'],'unprocessable')
        self.assertEqual(data['success'], False)

    def test_search(self):
        search_term = {'searchTerm': 'actor'}
        res = self.client().post('questions/search', 
        data=json.dumps(search_term),
        content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['questions'], list)
        self.assertIsInstance(data['total_questions'], int)
    
    def test_search_fail(self):
        search_term = {'searchTerm': ''}
        res = self.client().post('/questions/search',
        data=json.dumps(search_term),
        content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_get_questions_by_category(self):    
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(data['questions'], list)
        self.assertIsInstance(data['total_questions'], int)
        self.assertEqual(data['current_category'], 1)
        for question in data['questions']:
            self.assertEqual(question['category'],1)

    def test_get_questions_by_category_fail(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "resource not found")
    
    def test_get_quiz_questions(self):
        res = self.client().post('/quizzes', 
        data=json.dumps(self.quiz_data),
        content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        if data.get('question', None):
            self.assertNotIn(data['question']['id'],self.quiz_data['previous_questions'])
    
    def test_get_quiz_questions_fail(self):
        res = self.client().post('/quizzes',
        data=json.dumps({}),
        content_type='application/json')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data["message"], "bad request")



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()