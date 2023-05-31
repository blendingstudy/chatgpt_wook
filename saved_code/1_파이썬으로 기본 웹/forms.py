```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField("제목", validators=[DataRequired()])
    content = TextAreaField("내용", validators=[DataRequired()])
```