from flask import Flask, render_template, request
from src.tokens import Tokens
from src.validator import Validator
import sys


app = Flask(__name__, template_folder="src/templates")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    elif request.method == 'POST':
        expression = request.form['expression'].replace("\r", "")
        expressions = list(filter(None, expression.split("\n")))
        tokens = Tokens()
        validated_lexems = []
        line = 1
        for exp in expressions:
            validated_lexems.extend(list(map(
                lambda ci, ce, d: (
                    list(d.keys()).pop(), list(d.values()).pop(), 'Yes' if list(d.values()).pop() is not None else 'No', line, str(ci)+"-"+str(ce)),
                *zip(*tokens.split_token(exp))
            )))
            line += 1
        return render_template("index.html", input=expression, validated_lexems=validated_lexems)


if __name__ == '__main__':
    app.run(debug=True)
