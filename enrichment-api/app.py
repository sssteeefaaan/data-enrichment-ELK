from flask import Flask, Response
from json import dumps
from os import environ

app = Flask(__name__)

@app.route("/enrich", methods=["GET"])
def enrich():
    return Response(
        dumps({
            "enriched_field": "This is a newly added field" 
        }),
        status=200,
        mimetype= "json"
    )

if __name__ == "__main__":
    app.run(debug=True, port=int(environ.get("PORT", "9999")))