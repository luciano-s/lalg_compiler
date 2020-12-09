from flask import Flask, render_template, request
from flask import jsonify
from src.analyzers import Analyzers

app = Flask(__name__, template_folder="src/templates")


@app.route("/compiler/lexical_analyzer", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        expression = request.form["expression"]
        validated_lexems = Analyzers.lexical_analyzer(expression)

        return render_template(
            "index.html",
            input=expression,
            validated_lexems=validated_lexems,
        )


@app.route("/compiler/syntax_analyzer", methods=["GET", "POST"])
def syntax_analyzer():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        expression = request.form["expression"]
        leaf_tokens = Analyzers.lexical_analyzer(expression=expression)
        print(f"leaf_tokens(app): {leaf_tokens}")
        # input()
        tokens = Analyzers.syntax_analyzer(validated_lexems=leaf_tokens)
        print(f"tokens (app): {tokens}")

        return render_template(
            "syntax_analyzer.html",
            input=expression,
            tokens=tokens,
        )


if __name__ == "__main__":
    app.run(debug=True, port=9000)
