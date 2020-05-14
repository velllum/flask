from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    query = StringField('Query', validators=[DataRequired('Задан пустой поисковый запрос')])
    submit = SubmitField('найти')

class SearchFormResult(FlaskForm):
    result_search_data = StringField('result', validators=[DataRequired('Задан пустой поисковый запрос'),
                                                    Length(min=4, message='Поле должно содержать не менее 4 символов'),
                                                    Length(max=25, message='Поле должно содержать не более 25 символов')
                                                    ])
