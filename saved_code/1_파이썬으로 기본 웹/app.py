```python
from flask import Flask
from routes import bp_home, bp_post
from database import init_database
from models import Post

app = Flask(__name__)
app.register_blueprint(bp_home)
app.register_blueprint(bp_post)

if __name__ == "__main__":
  init_database()
  app.run(debug=True)
```