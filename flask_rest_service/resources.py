import json
import urllib
from lxml import html
from flask import request, abort
from flask.ext import restful
from flask.ext.restful import reqparse
from flask_rest_service import app, api, mongo
from bson.objectid import ObjectId

DEWICK = "11&locationName=Dewick-MacPhie+Dining+Center"
CARM = "09&locationName=Carmichael+Dining+Center"
ERROR = { "error": "Resource not found." }

class Menu(restful.Resource):
    def get(self, hall, day, month, year):

        if hall == "carm":
            hall = CARM
        elif hall == "dewick":
            hall = DEWICK
        else:
            return ERROR

        page = urllib.urlopen("http://menus.tufts.edu/foodpro/shortmenu.asp?sName=Tufts+Dining&locationNum=" + hall + "&naFlag=1&WeeksMenus=This+Week%27s+Menus&myaction=read&dtdate=" + month + "%2F" + day + "%2F" + year)
        htmlSource = page.read()
        tree = html.fromstring(htmlSource)
        return self.getdata(tree)

    def getdata(self, tree):
        jsondata = {}
        for meal in tree.findall(".//*[@class='shortmenumeals']"):
            curr_meal = meal.text
            jsondata[curr_meal] = {}
            mealparent = meal.find("../../../../../../..")
            for foodtype in mealparent.findall(".//*[@class='shortmenucats']/span"):
                curr_foodtype = foodtype.text[3:-3]
                jsondata[curr_meal][curr_foodtype] = []
                for food in foodtype.xpath("../../../following-sibling::tr"):
                    if food.find(".//*[@name='Recipe_Desc']") is None:
                        break
                    jsondata[curr_meal][curr_foodtype].append(food.find(".//*[@name='Recipe_Desc']").text)
        return jsondata

api.add_resource(Menu, '/<hall>/<day>/<month>/<year>')
