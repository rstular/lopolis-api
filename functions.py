import json

from bs4 import BeautifulSoup
from flask import Response

HOST = "https://www.lopolis.si"


def About():
    info = {}
    info["error"] = False
    info["status_code"] = 200
    info["author"] = "Rok Stular"
    info["author_website"] = "https://rstular.github.io/"
    info["documentation"] = "https://rstular.github.io/projects/lopolis.html"
    info["license"] = "https://github.com/rstular/lopolis-api/blob/master/LICENSE"
    info["source"] = "https://github.com/rstular/lopolis-api"
    info["bug_reports"] = "https://github.com/rstular/lopolis-api/issues"
    info["changelog"] = "https://github.com/rstular/lopolis-api/blob/master/CHANGELOG.md"
    info["version"] = "1.0.9"
    return info


Unauthorized = {"error": True, "status_code": 401, "message": "Unauthorized"}
BadRequest = {"error": True, "status_code": 400, "message": "Bad request"}


def OtherError(status_code):
    return {"error": True, "status_code": status_code}


def Success(data=None):
    return {"error": False, "status_code": 200} if data is None else {"error": False, "status_code": 200, "data": data}


def Get_RVT_Oseba(input_forms, action):
    osebaModel = ""
    verificationToken = ""
    for form in input_forms:

        if form["action"] == action:
            for inputField in form.find_all("input"):
                if inputField.get("name") == "__RequestVerificationToken":
                    verificationToken = inputField.get("value")
                    break

            for selectField in form.find_all("select"):
                if selectField.get("id") == "OsebaModel_ddlOseba":
                    osebaModel = selectField.contents[0].get("value")
                    break
            break

    return verificationToken, osebaModel


def JSONResponse(input_dict):
    return Response(json.dumps(input_dict), status=input_dict["status_code"], mimetype="application/json")
