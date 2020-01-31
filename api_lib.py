import requests
from bs4 import BeautifulSoup

from functions import *

import json


def GetToken(username, password):

    sess = requests.Session()
    response = sess.get(HOST)

    soup = BeautifulSoup(response.text, "html.parser")

    verificationToken = ""

    for form in soup.find_all("form"):
        if form["action"] == "/Uporab/Prijava":
            for inputField in form.find_all("input"):
                if inputField["name"] == "__RequestVerificationToken":
                    verificationToken = inputField["value"]
                    break

    json_data = {"__RequestVerificationToken": verificationToken, "Uporabnik": username,
                 "Geslo": password, "OsveziURL": "https://www.lopolis.si/", "X-Requested-With": "XMLHttpRequest"}

    response = sess.post(HOST, data=json_data)

    if response.status_code == 200:
        if ".LopolisPortalAuth" in sess.cookies.get_dict():
            return {"error": False, "data": sess.cookies.get_dict()[".LopolisPortalAuth"], "status_code": 200}
        else:
            return Unauthorized
    else:
        return {"error": True, "status_code": response.status_code}


def GetMenus(login_token, year, month):

    sess = requests.Session()
    sess.get(HOST)

    sess_cookies = sess.cookies.get_dict()
    sess_cookies[".LopolisPortalAuth"] = login_token
    response = sess.get(HOST + "/?MeniZgorajID=6&MeniID=78",
                        cookies=sess_cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    verificationToken, osebaModel = Get_RVT_Oseba(
        soup.find_all("form"), "/Prehrana/Prednarocanje")
    del(soup)

    try:
        osebaID, osebaTip, ustanovaID = osebaModel.split(";")
    except:
        return Unauthorized

    json_data = {"__RequestVerificationToken": verificationToken, "Ukaz": "", "OsebaModel.ddlOseba": osebaModel, "OsebaModel.OsebaID": osebaID,
                 "OsebaModel.OsebaTipID": osebaTip, "OsebaModel.UstanovaID": ustanovaID, "MesecModel.Mesec": month, "MesecModel.Leto": year, "X-Requested-With": "XMLHttpRequest"}
    response = sess.post(HOST + "/?MeniZgorajID=6&MeniID=78",
                         data=json_data, cookies=sess_cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    for form in soup.find_all("form"):

        if form["action"] == "/Prehrana/Prednarocanje":

            tbody = form.find("table").tbody
            menu = {}

            for tr in tbody.find_all("tr"):

                dayOutput = {}
                tds = tr.find_all("td")

                dayOutput["meal"] = tds[1].contents[0].split("\r")[0]
                dayOutput["menu_type"] = tds[2].contents[0].split("\r")[0]
                dayOutput["location"] = tds[3].contents[0].split("\r")[0]
                dayOutput["menu_options"] = []

                menuContent = tds[4].contents
                menuOptions = [x for x in menuContent[0].contents if x != "\n"]

                date = menuContent[2]["value"]
                empty = False

                if menuContent[0].get("readonly") != "readonly":

                    dayOutput["readonly"] = False

                    if len(menuOptions) > 1:

                        for option in menuOptions:

                            if option.get("value") != "":

                                menuOutput = {"value": option.get(
                                    "value"), "text": option.contents[0]}
                                menuOutput["selected"] = not option.get(
                                    "selected") is None
                                dayOutput["menu_options"].append(menuOutput)

                    else:
                        empty = True
                else:
                    menuOutput = None
                    for option in menuOptions:
                        if not option.get("value") == "" and not option.get("selected") is None and not option.contents[0] == "":
                            menuOutput = {"value": option.get(
                                "value"), "text": option.contents[0]}
                            dayOutput["readonly"] = True

                    if not menuOutput is None:
                        dayOutput["menu_options"].append(menuOutput)
                    else:
                        empty = True

                if not empty:
                    menu[date] = dayOutput

            return Success(menu)
    return Unauthorized


def GetCheckouts(login_token, year, month):

    sess = requests.Session()
    sess.get(HOST)

    sess_cookies = sess.cookies.get_dict()
    sess_cookies[".LopolisPortalAuth"] = login_token
    response = sess.get(HOST + "/?MeniZgorajID=6&MeniID=77",
                        cookies=sess_cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    verificationToken, osebaModel = Get_RVT_Oseba(
        soup.find_all("form"), "/Prehrana/Odjava")
    del(soup)

    try:
        osebaID, osebaTip, ustanovaID = osebaModel.split(";")
    except:
        return Unauthorized

    json_data = {"__RequestVerificationToken": verificationToken, "Ukaz": "", "OsebaModel.ddlOseba": osebaModel, "OsebaModel.OsebaID": osebaID,
                 "OsebaModel.OsebaTipID": osebaTip, "OsebaModel.UstanovaID": ustanovaID, "MesecModel.Mesec": month, "MesecModel.Leto": year, "X-Requested-With": "XMLHttpRequest"}
    response = sess.post(HOST + "/?MeniZgorajID=6&MeniID=77",
                         data=json_data, cookies=sess_cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    for form in soup.find_all("form"):

        if form["action"] == "/Prehrana/Odjava":

            tbody = form.find("table").tbody
            checkouts = {}

            for tr in tbody.find_all("tr"):

                tds = tr.find_all("td")
                checkbox_contents = [x for x in tds[3].contents if x != "\n"]
                date = checkbox_contents[2]["value"]

                if not checkbox_contents[0].get("checked") is None:
                    checkouts[date] = tds[1].contents[0].split("\r")[0]

            return Success(checkouts)

    return Unauthorized


def SetCheckouts(login_token, choices):

    if len(choices) > 31 or len(choices) < 1:
        return BadRequest

    months = {}
    for month in list(choices):
        if len(months) > 2:
            return BadRequest
        months[month.split("-")[1].strip("0")] = month.split("-")[0]

    sess = requests.Session()

    response = sess.get(HOST)

    sess_cookies = sess.cookies.get_dict()
    sess_cookies[".LopolisPortalAuth"] = login_token
    response = sess.get(HOST + "/?MeniZgorajID=6&MeniID=77",
                        cookies=sess_cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    verificationToken, osebaModel = Get_RVT_Oseba(
        soup.find_all("form"), "/Prehrana/Odjava")
    del(soup)

    try:
        osebaID, osebaTip, ustanovaID = osebaModel.split(";")
    except:
        return Unauthorized

    res_code = 200

    for month in months:

        json_data = {"__RequestVerificationToken": verificationToken, "Ukaz": "", "OsebaModel.ddlOseba": osebaModel, "OsebaModel.OsebaID": osebaID,
                     "OsebaModel.OsebaTipID": osebaTip, "OsebaModel.UstanovaID": ustanovaID, "MesecModel.Mesec": month, "MesecModel.Leto": months[month], "X-Requested-With": "XMLHttpRequest"}
        response = sess.post(HOST + "/?MeniZgorajID=6&MeniID=77",
                             data=json_data, cookies=sess_cookies)

        soup = BeautifulSoup(response.text, "html.parser")

        dateIndexing = {}

        for form in soup.find_all("form"):

            if form["action"] == "/Prehrana/Odjava":

                for inputField in form.find_all("input"):
                    if inputField.get("name") == "__RequestVerificationToken":
                        verificationToken = inputField.get("value")
                        break

                json_data = {"__RequestVerificationToken": verificationToken, "Shrani": "Shrani", "Ukaz": "Shrani", "OsebaModel.ddlOseba": osebaModel, "OsebaModel.OsebaID": osebaID,
                             "OsebaModel.OsebaTipID": osebaTip, "OsebaModel.UstanovaID": ustanovaID, "MesecModel.Mesec": month, "MesecModel.Leto": months[month], "X-Requested-With": "XMLHttpRequest"}

                tbody = form.find("table").tbody

                for tr in tbody.find_all("tr"):

                    tds = tr.find_all("td")

                    checkboxContent = [x for x in tds[3].contents if x != "\n"]

                    if not checkboxContent[2].get("value") in dateIndexing:
                        dateIndexing[checkboxContent[2].get("value")] = {}
                    dateIndexing[checkboxContent[2].get("value")][tds[1].contents[0].split("\r")[
                        0]] = checkboxContent[2].get("id").split("_")[1]

                    for inputField in checkboxContent:
                        pass
                        if not "CheckOut" in inputField.get("name"):
                            json_data[inputField.get(
                                "name")] = inputField.get("value")
                        else:
                            json_data[inputField.get("name")] = "false"

                for date in choices:
                    try:
                        json_data["OdjavaItems[%s].CheckOut" %
                                  dateIndexing[date][choices[date]]] = ["true", "false"]
                    except KeyError:
                        return BadRequest

                response_status = sess.post(
                    HOST + "/Prehrana/Odjava", data=json_data, cookies=sess_cookies).status_code
                if response_status != 200:
                    res_code = response_status

    return Success() if res_code == 200 else OtherError(res_code)


def SetMenus(login_token, choices):

    if len(choices) > 31 or len(choices) < 1:
        return BadRequest

    months = {}
    for month in list(choices):
        if len(months) > 2:
            return BadRequest
        months[month.split("-")[1].strip("0")] = month.split("-")[0]

    sess = requests.Session()

    response = sess.get(HOST)

    sess_cookies = sess.cookies.get_dict()
    sess_cookies[".LopolisPortalAuth"] = login_token
    response = sess.get(HOST + "/?MeniZgorajID=6&MeniID=78",
                        cookies=sess_cookies)

    soup = BeautifulSoup(response.text, "html.parser")
    verificationToken, osebaModel = Get_RVT_Oseba(
        soup.find_all("form"), "/Prehrana/Prednarocanje")
    del(soup)

    try:
        osebaID, osebaTip, ustanovaID = osebaModel.split(";")
    except:
        return Unauthorized

    res_code = 200

    for month in months:

        json_data = {"__RequestVerificationToken": verificationToken, "Ukaz": "", "OsebaModel.ddlOseba": osebaModel, "OsebaModel.OsebaID": osebaID,
                     "OsebaModel.OsebaTipID": osebaTip, "OsebaModel.UstanovaID": ustanovaID, "MesecModel.Mesec": month, "MesecModel.Leto": months[month], "X-Requested-With": "XMLHttpRequest"}
        response = sess.post(HOST + "/?MeniZgorajID=6&MeniID=78",
                             data=json_data, cookies=sess_cookies)

        soup = BeautifulSoup(response.text, "html.parser")

        dateIndexing = {}

        for form in soup.find_all("form"):

            if form["action"] == "/Prehrana/Prednarocanje":

                for inputField in form.find_all("input"):
                    if inputField.get("name") == "__RequestVerificationToken":
                        verificationToken = inputField.get("value")
                        break

                json_data = {"__RequestVerificationToken": verificationToken, "Shrani": "Shrani", "Ukaz": "Shrani", "OsebaModel.ddlOseba": osebaModel, "OsebaModel.OsebaID": osebaID,
                             "OsebaModel.OsebaTipID": osebaTip, "OsebaModel.UstanovaID": ustanovaID, "MesecModel.Mesec": month, "MesecModel.Leto": months[month], "X-Requested-With": "XMLHttpRequest"}

                tbody = form.find("table").tbody

                for tr in tbody.find_all("tr"):

                    tds = tr.find_all("td")

                    menuContent = [x for x in tds[4].contents if x != "\n"]

                    for inputField in menuContent:
                        if inputField.name == "input":
                            fieldID = inputField.get("id").split("_")
                            json_data["PrednarocanjeItems[%s].%s" % (fieldID[1], fieldID[3].replace(
                                "ABO", "ABO_PrijavaID"))] = inputField.get("value")
                            if fieldID[3] == "Datum":
                                dateIndexing[inputField.get(
                                    "value")] = fieldID[1]

                temp_json_data = {}

                for json_header in json_data:
                    if "ReadOnly" in json_header and json_data[json_header] == "False":
                        headerID = json_header.split("[")[1].split("]")[0]
                        temp_json_data["PrednarocanjeItems[%s].MeniIDSkupinaID" %
                                       headerID] = ""

                for entry in temp_json_data:
                    json_data[entry] = temp_json_data[entry]

                del(temp_json_data)

                for date in choices:
                    index = dateIndexing[date]
                    json_data["PrednarocanjeItems[%s].MeniIDSkupinaID" %
                              index] = choices[date]

                response_status = sess.post(
                    HOST + "/Prehrana/Prednarocanje", data=json_data, cookies=sess_cookies).status_code
                if response_status != 200:
                    res_code = response_status

    return Success() if res_code == 200 else OtherError(res_code)
