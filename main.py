import json
import os

from flask import Flask, redirect, request
from flask_cors import CORS, cross_origin
from user_agents import parse

import api_lib
from functions import About, BadRequest, JSONResponse
from helpers import GetCoffee, HTMLGetCoffee, ImATeapot

app = Flask(__name__)
CORS(app)


@app.route("/gettoken", methods=["POST"])
@cross_origin()
def gettoken():

    content = request.get_json()

    if content is None:
        return JSONResponse(BadRequest)

    if len(content) == 2 and "username" in content and "password" in content:
        login_result = api_lib.GetToken(content["username"], content["password"])
        return JSONResponse(login_result)
    else:
        return JSONResponse(BadRequest)


@app.route("/getmenus", methods=["POST"])
@cross_origin()
def getmenus():

    content = request.get_json()

    if content is None:
        return JSONResponse(BadRequest)

    if (
        len(content) == 2
        and "year" in content
        and "month" in content
        and not request.headers.get("Authorization") is None
    ):
        try:
            authorization_token = request.headers.get("Authorization").split("Bearer ")[
                1
            ]
            if len(authorization_token) != 288:
                raise ValueError("Token not the right length")
        except:
            return JSONResponse(BadRequest)

        menus_result = api_lib.GetMenus(
            authorization_token, content["year"], content["month"]
        )
        return JSONResponse(menus_result)
    else:
        return JSONResponse(BadRequest)


@app.route("/getcheckouts", methods=["POST"])
@cross_origin()
def getcheckouts():

    content = request.get_json()

    if content is None:
        return JSONResponse(BadRequest)

    if (
        len(content) == 2
        and "year" in content
        and "month" in content
        and not request.headers.get("Authorization") is None
    ):
        try:
            authorization_token = request.headers.get("Authorization").split("Bearer ")[
                1
            ]
            if len(authorization_token) != 288:
                raise ValueError("Invalid token length")
        except:
            return JSONResponse(BadRequest)

        checkouts_result = api_lib.GetCheckouts(
            authorization_token, content["year"], content["month"]
        )
        return JSONResponse(checkouts_result)
    else:
        return JSONResponse(BadRequest)


@app.route("/setmenus", methods=["POST"])
@cross_origin()
def setmenus():

    content = request.get_json()

    if content is None:
        return JSONResponse(BadRequest)

    if (
        len(content) == 1
        and "choices" in content
        and not request.headers.get("Authorization") is None
    ):
        try:
            authorization_token = request.headers.get("Authorization").split("Bearer ")[
                1
            ]
            if len(authorization_token) != 288:
                raise ValueError("Invalid token length")
        except:
            return JSONResponse(BadRequest)

        menus_result = api_lib.SetMenus(authorization_token, content["choices"])
        return JSONResponse(menus_result)

    else:
        return JSONResponse(BadRequest)


@app.route("/setcheckouts", methods=["POST"])
@cross_origin()
def setcheckouts():

    content = request.get_json()

    if content is None:
        return JSONResponse(BadRequest)

    if (
        len(content) == 1
        and "checkouts" in content
        and not request.headers.get("Authorization") is None
    ):
        try:
            authorization_token = request.headers.get("Authorization").split("Bearer ")[
                1
            ]
            if len(authorization_token) != 288:
                raise ValueError("Invalid token length")
        except:
            return JSONResponse(BadRequest)

        checkouts_result = api_lib.SetCheckouts(
            authorization_token, content["checkouts"]
        )
        return JSONResponse(checkouts_result)

    else:
        return JSONResponse(BadRequest)


@app.route("/about", methods=["GET"])
@cross_origin()
def version():
    return JSONResponse(About())


@app.route("/", methods=["GET"])
def root():
    return redirect(About()["documentation"], code=302)


@app.errorhandler(404)
@cross_origin()
def handler(e):
    return JSONResponse({"error": True, "status_code": 404, "message": "Not found"})


@app.route("/coffeepot", methods=["GET"])
@cross_origin()
def getcoffee():
    parsed_ua = parse(request.headers.get("User-Agent"))
    if parsed_ua.is_pc or parsed_ua.is_tablet or parsed_ua.is_mobile:
        return HTMLGetCoffee()
    else:
        return JSONResponse(GetCoffee)


@app.route("/teapot")
@cross_origin()
def teapot():
    return JSONResponse(ImATeapot)


if __name__ == "__main__":
    app.run(port=80)
