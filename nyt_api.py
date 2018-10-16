import os
import json
import sys
import requests
from top_story import TopStory
import mysql.connector as mc


class MyApp:

    def dispatch(self, environ):
        query = environ['QUERY_STRING']
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']

        if method == 'GET' and path=="/stories":
            return json.dumps(self.get_resuslts())
            # do something
        elif method == 'GET' and path == "/load":
            return json.dumps(self.retrieve_top_stories())

        return "Your request is invalid, please try new URL"


    def retrieve_top_stories(self):
        r = requests.get("http://api.nytimes.com/svc/topstories/v2/home.json?api-key=835661c5274a4972b20d661cbea8e281",
            json=True)
        data_dict= r.json()
        list_of_results = data_dict['results']
        list_of_custome_top_stories = []

        for article in list_of_results:
            title = article['title']
            abstract = article['abstract']
            published_date = article['published_date']
            short_url = article['short_url']
            image_url = ""

            for image in article['multimedia']:
                if image['format'] == 'superJumbo':
                    image_url = image['url']
                else:
                    image_url = article['multimedia'][0]['url']



            obj = TopStory(title, abstract, published_date, short_url, image_url)
            self.data_insert(obj)
            list_of_custome_top_stories.append(obj)

        return data_dict


    def data_insert(self, topstory):
        mydb = self.open_db()
        try:
            mycursor = mydb.cursor()
            insert = "INSERT INTO topstories(title, abstract, published_date, short_url, image_url) VALUES (%s, %s, %s, %s, %s)"
            _tuple_of_values = (topstory.title, topstory.abstract, topstory.published_date, topstory.short_url, topstory.image_url)

            mycursor.execute(insert, _tuple_of_values)
            mydb.commit()
        except Exception as exc:
            print(exc)
        finally:
            mycursor.close()
            self.close_db(mydb)


    def get_resuslts(self):
        mydb = self.open_db()
        mycursor = mydb.cursor()
        try:

            mycursor.execute("SELECT * FROM topstories")

            myresult = mycursor.fetchall()

            return myresult

        except Exception as exc:
            print(exc)

        finally:
            mycursor.close()
            self.close_db(mydb)

        return myresult


    def open_db(self):
        mydb = mc.connect(
            host="localhost",
            user=os.environ['USER'],
            password=os.environ['PASSWORD'],
            database=os.environ['NAME'],
            )

        return mydb


    def close_db(self, mydb):
        mydb.close()
