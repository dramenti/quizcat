import re
import os
import json
import sqlite3

class Tossup:
    def __init__(self, Tournament, Year, Round, Number, Category, Subcategory, ID, Question, Answer):
        """
        Constructs a Tossup object from the string parameters:
        Tournament, Year, Round, Number, Category, Subcategory,
        Question, Answer.
        Each field is stripped of whitespace with str.strip method
        """
        self.Tournament = Tournament.strip()
        self.Year = Year.strip()
        self.Round = Round.strip()
        self.Number = Number.strip()
        self.Category = Category.strip()
        self.Subcategory = Subcategory.strip()
        self.Question = Question.strip()
        self.Answer = Answer.strip()
        self.ID = ID.strip()
    def as_tuple(self):
        """
        Returns Tossup as a tuple 
        """
        return (self.Tournament, self.Year, self.Round, self.Number, self.Category, self.Subcategory, self.ID, self.Question, self.Answer)
    def as_dictionary(self):
        """
        Returns Tossup as a dictionary, making it serializable
        """
        return {
            "Tournament": self.Tournament,
            "Year": self.Year,
            "Round": self.Round,
            "Number": self.Number,
            "Category": self.Category,
            "Subcategory": self.Subcategory,
            "Question": self.Question,
            "Answer": self.Answer,
            "ID": self.ID
        }
#note: only handles 1 subcategory at a time
def parsing(filename):
    s = None
    with open(filename) as f:
        s = f.read()
    regex_tossup = re.compile(r'<p><b>Result: \d+ \| ([^\|]+) \| (\d+) \| Round: [^0-9]*(\d*)[^\|]*\| Question: (\d+) \| ([^\|]+) \| ([^<]+)</b>[^I]+ID:\s(\d+)[^Q]+Question:</em>\s([^<]+)[^A]+ANSWER:</strong></em>\s([^<]+)')
    #control groups for tossup are: Tournament, Year, Round, Question Number, Category, Subcategory, Question, Answer
    matches = regex_tossup.findall(s)
    print("Number of matches: ", len(matches))

    tossups = map(lambda t: tuple(map(str.strip, t)), matches) #apply strip to data
    return list(tossups)
    #for m in matches:
     #   tossups.append(Tossup(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7], m[8]))
    #tuple_tossups = map(Tossup.as_tuple, tossups) 
    #return tuple_tossups
    #the following is commented out; it is for database-less storage with json
    #(i.e. PLEASE IGNORE)
    """
    catsubcat = (json_tossups[0]['Category'], json_tossups[0]['Subcategory'])
    for t in json_tossups:
        if (t['Category'], t['Subcategory']) != catsubcat:
            print("Category error: expected", catsubcat, "but got", (t['Category'], t['Subcategory']))
            return None
    with open('Database/' + catsubcat [0] + '/' + catsubcat[1] + '/' + catsubcat[1] + '.json', 'w') as out:
        json.dump(json_tossups, out, sort_keys = True, indent = 4, ensure_ascii=False)
    """
def storeTossups(filename):
    tossups = parsing(filename)
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    query = "INSERT INTO Tossups (Tournament, Year, Round, Number, Category, Subcategory, ID, Question, Answer) VALUES (?,?,?,?,?,?,?,?,?)"
    c.executemany(query, tossups)
    conn.commit()
    conn.close()
def displayTossups():
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("SELECT Answer FROM Tossups")
    conn.commit()
    data = c.fetchall()
    print('Length of data: ', len(data))
    print(data)
    conn.close()
def executeQuery(query): #use with caution 
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute(query)
    conn.commit()
    data = c.fetchall()
    conn.close()
    return data
def deleteTossups():
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    c.execute("DELETE FROM Tossups")
    conn.commit()
    conn.close()

def thises(data):
    thiswords = list()
    regex = re.compile(r'this (\w+)')
    for each in data:
        matches = regex.findall(each[0])
        thiswords += matches
    return thiswords

def learn(): 
    conn = sqlite3.connect('db.sqlite')
    c = conn.cursor()
    query = "SELECT Question, Answer FROM Tossups WHERE Category=:category AND Subcategory=:subcategory"
    fulljso = dict()
    datafile = 'data.json'
    categories = [('Literature', 'American')]
    for category, subcategory in categories:
        c.execute(query, {'category': category, 'subcategory': subcategory})
        conn.commit()
        data = c.fetchall()
        jso = dict() #java script object
        jso['Name'] = category+subcategory 
        #jso['Category'] = category
        jso['This'] = thises(data)
        jso['Answerline'] = [tossup[1] for tossup in data] #all the answerlines
        fulljso[jso['Name']] = jso
    with open(datafile, 'w') as f:
        json.dump(fulljso, f)

#returns the length of the 'pseudo-intersection' of list A (short list) and B. duplicates are counted, hence 'pseudo' intersection
def similarity(a, b):
    sim = 0
    for word in b:
        sim += a.count(word)
    return sim

def recognize(q, a):
    l = list()
    with open('data.json') as f:
        l = json.load(f)
    similarity_points = dict()
    thiswords = thises([(q,)])
    print('Thiswords: ', thiswords)
    for category in l:
        similarity_points[l[category]['Name']] = similarity(thiswords, l[category]['This']) + l[category]['Answerline'].count(a)
        #similarity_points[category['Name']] = len(set(thiswords).intersection(set(category['This']))) + len([answer for answer in category['Answerline'] if answer==a])
    return similarity_points










