#region Imports
import os
import re
import sys
import time
import json
import pymongo
import encodings
from datetime import datetime
import encodings
from datetime import datetime
from nltk import PorterStemmer
from nltk.corpus import stopwords
from nltk.tag.stanford import StanfordNERTagger
#endregion

#region Initialisation
Current_Path = "./Source Code/"
LogDir = Current_Path + "Logs/"

#Setting variables
stemmer = PorterStemmer() #Initialising the stemmer
java_path = "C:/Program Files/Java/jdk1.8.0_92/bin"
os.environ['JAVAHOME'] = java_path

lstTrackingFor = ["#MSF", "#πρόσφυγες", "#πρόσφυγες",  "#προσφυγικό",  "#προσφυγικο","πρόσφυγες", "πρόσφυγες",  "προσφυγικό",  "προσφυγικο",
"prosfiges", "prosfiges",  "prosfigiko",  "prosfygiko",  "#RefugeeCrisis", "migrants", "migration crisis",  "migration flow",  "refugees", "#RefugeeCrisis", "#refugeesGr",
"#refugeeswelcome",  "#WelcomeRefugees",  "#ProMuslimRefugees", "asylum seekers",  "human rights",  "#helpiscoming",  "solidarity", "#solidaritywithrefugees",  "Balkan route",
"irregular migrants",  "borders", "open borders", "border closure", "border share",  "No borders",  "#OpentheBorders", "Syria",  "Iraq", "Afghanistan", "Pakistan", "islamists",
"ISIS",  "daesh", "muslims",  "Idomeni",  "Calais",  "Lesbos", "Lesvos", "Lesbosisland", "migrant camps", "refugee camps", "#safepassage", "rapefugees", "#antireport ", "Aylan",
"European Mobilisation", "Amnesty International", "Frontex",  "UNHCR", "UN Refugee Agency", "#FortressEurope", "@MovingEurope"]

#Connect to a MongoDB Database
MongoDBCon = pymongo.MongoClient() #Lack of arguments defaults to localhost:27017
MongoDBDatabase = MongoDBCon["RefugeeCrisisCon"]
RawTweetsJSON_coll = MongoDBDatabase["RawTweetsJSON"]
ProcessedTweets_coll = MongoDBDatabase['Edges_Processed_Tweet']
UsersEdges_coll = MongoDBDatabase['Edges_Users']
EventsEdges_coll = MongoDBDatabase['Edges_Events']
HashtagsEdges_coll = MongoDBDatabase['Edges_Hashtag']

##Variables for the Greek Stemmer
#Greek_Stopwords_file = open(Current_Path + "Settings/Greek_Stopwords.JSON")
#Greek_Stopwords = json.load(Greek_Stopwords_file)["stopwrods"]

#Step1List_file = open(Current_Path + "Settings/Greek_Stemming/Step1List.JSON")
#Step1List = json.load(Step1List_file)

#Step1RegExp_file = open(Current_Path + "Settings/Greek_Stemming/Step1RegExp.txt")
#Step1RegExp = Step1RegExp_file.read()

#v_file = open(Current_Path + "Settings/Greek_Stemming/v.txt")
#v = v_file.read()

#v2_file = open(Current_Path + "Settings/Greek_Stemming/v2.txt")
#v2 = v2_file.read()
#endregion

#region Functions
##Returns a string that has been normalised in terms of Natural Language Processing
##[input: string] [output: string]
#def normaliseText(text):
#    result = text
#    dirtyChars = ['ά','έ','ό','ή','ί','ύ','ώ','ς']
#    cleanChars = ['α','ε','ο','η','ι','υ','ω','σ']
#    for i in range(0, len(dirtyChars)):
#        result = str.replace(result, dirtyChars[i], cleanChars[i])
#    return result

#Removes the TextToRemove from a text
#[input: string, string] [output: string]
def removeTextFromText(text, TextToRemove):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if TextToRemove not in word])
    return text

#Returns a list of words that starts with the input pattern like "#","http" etc.
#[input: list, string] [output: list]
def getWordsStartingWith(words, startsWith):
    result = list()
    length = len(startsWith)
    for i in range(0, len(words)):
        word = words[i].strip()
        if word[:length] == startsWith:
            result.append(words[i])
    return result

#Removes the stopwords from a text (warning: the input string must be in lowercase)
#[input: string, list] [output: string]
def removeStopwords(text, StopwordsList):
    words = SentenceStringStrip(text).split(" ")
    result = ' '.join([word for word in words if word not in StopwordsList])
    return result

#Checks whether the input is in English
#[input: string] [output: boolean]
def isEnglish(text):
    try:
        text.encode('ascii')
    except UnicodeEncodeError:
        return False
    else:
        if hasNumbers(text):
            return False
        else:
            return True

#Removes non English words
#[input: string] [output: list]
def removeNonEnglishText(text):
    result = list()
    words = text.strip().split(" ")

    for i in range(0, len(words)):
        if isEnglish(words[i]) == True:
            result.append(words[i])

    return result

#Removes the list items from a text
#[input: string, list] [output: string]
def removeListItemsFromText(text, lst):
    words = text.strip().split(" ")
    text = ' '.join([word for word in words if word not in lst])
    return text

#Removes the list items from a text
#[input: string, list] [output: string]
def eraseListItemsFromText(text, lst):
    for item in lst:
        text = text.replace(item, "")
    return text

#Removes the superfluous space characters
#[input: string] [output: string]
def SentenceStringStrip(text):
    words = text.strip().split(" ")
    result = ' '.join(word.strip() for word in words if word.strip())
    return result

#Removes Special Characters from a string
#[input: string] [output: string]
def removeSpecialCharsFromText(text):
    dirtyChars = [',', '.', ';', '?', '/', '\\', '`', '[', ']', '"', ':', '>', '<', '|', '-', '_', '=', '+', '(', ')', '^', '{', '}', '~', '\'', '*', '&', '%', '$', '!', '@', '#']
    for i in range(0, len(dirtyChars)):
        text = str.replace(text, dirtyChars[i], " ")
    result = SentenceStringStrip(text)
    return result

#Replaces all the occurrences of a dictionary's name with the corresponding value
#[input: string, dictionary] [output: string]
def replace_all(text, dic):
    for i, j in iter(dic.items()):
        text = text.replace(i, j)
    return text

#Returns boolean depending on whether a string contains any numbers
#[input: string] [output: boolean]
def hasNumbers(String):
    return any(char.isdigit() for char in String)

#Returns the screenname of the person who made the original tweet (from a retweet)
#[input: string] [output: string]
def getRetweetedFromScreenname(TweetText):
    result = None
    Tweet = TweetText
    TweetWithoutRT = Tweet[3:]

    if Tweet[:3].lower() == "rt ":
        iStart = TweetWithoutRT.find("@")
        iEnd = TweetWithoutRT.find(":")

        if ((iStart == 0) and (iEnd != -1)):
            result = TweetWithoutRT[iStart:(iStart+iEnd)]
    return result

#Uses the Greek Stemming function stem on a sentence
#[input: string] [output: string]
def StemAll(text):
    words = text.strip().split(" ")
    result = ' '.join(stem(word) for word in words)
    return result

#Python implementation stemmer described by G. Ntais in his M.Sc Thesis
#http://people.dsv.su.se/~hercules/papers/Ntais_greek_stemmer_thesis_final.pdf
#[input: string (single word)] [output: string (single word)]
def stem(w):
    word = w
    stem = ""
    suffix = ""
    firstch = ""

    test1 = True

    if len(w) < 4:
        return w

    #step1

    RegularExpr = re.compile(Step1RegExp, re.U)
    Matches = RegularExpr.search(w)
    if Matches:
        stem = Matches.group(1)
        suffix = Matches.group(2)
        w = "{0}{1}".format(stem, Step1List[suffix])
        test1 = False

    re1 = "^(.+?)(αδεσ|αδων)$"
    re2 = "^(.+?)(εδεσ|εδων)$"
    re3 = "^(.+?)(ουδεσ|ουδων)$"
    re4 = "^(.+?)(εωσ|εων)$"

    #step 2
    RegularExpr = re.compile(re1, re.U)
    Matches = RegularExpr.search(w)
    if Matches: #step 2a
        stem = Matches.group(1)
        w = stem
        except1 = "(οκ|μαμ|μαν|μπαμπ|πατερ|γιαγι|νταντ|κυρ|θει|πεθερ)$"
        if re.search(except1, w, re.U) != True:
            w += "αδ"
    else:
        RegularExpr = re.compile(re2, re.U)
        Matches = RegularExpr.search(w)
        if Matches: #step 2b
            stem = Matches.group(1)
            w = stem
            except2 = "(οπ|ιπ|εμπ|υπ|γηπ|δαπ|κρασπ|μιλ)$"
            if re.search(except2, w, re.U):
                w += "εδ"
        else:
            RegularExpr = re.compile(re3, re.U)
            Matches = RegularExpr.search(w)
            if Matches: #step 2c
                stem = Matches.group(1)
                w = stem
                exept3 = "(αρκ|καλιακ|πεταλ|λιχ|πλεξ|σκ|σ|φλ|φρ|βελ|λουλ|χν|σπ|τραγ|φε)$"
                if re.search(exept3, w, re.U):
                    w += "ουδ"
            else:
                RegularExpr = re.compile(re4, re.U)
                Matches = RegularExpr.search(w)
                if Matches: #step 2d
                    stem = Matches.group(1)
                    w = stem
                    exept4 = "^(θ|δ|ελ|γαλ|ν|π|ιδ|παρ)$"
                    if re.search(exept4, w, re.U):
                        w += "ε"

    #step 3
    reCur = "^(.+?)(ια|ιου|ιων)$"
    RegularExpr = re.compile(reCur, re.U)
    Matches = RegularExpr.search(w)
    if Matches:
        stem = Matches.group(1)
        w = stem
        reCur = "" + v + "$";
        test1 = False
        if re.search(reCur, w, re.U):
            w = stem + "ι";

    #Step 4
    reCur = "^(.+?)(ικα|ικο|ικου|ικων)$"
    RegularExpr = re.compile(reCur, re.U)
    Matches = RegularExpr.search(w)
    if Matches:
        stem = Matches.group(1)
        w = stem
        test1 = False
        reCur = "" + v + "$";
        exept5 = "^(αλ|αδ|ενδ|αμαν|αμμοχαλ|ηθ|ανηθ|αντιδ|φυσ|βρωμ|γερ|εξωδ|καλπ|καλλιν|καταδ|μουλ|μπαν|μπαγιατ|μπολ|μποσ|νιτ|ξικ|συνομηλ|πετσ|πιτσ|πικαντ|πλιατσ|ποστελν|πρωτοδ|σερτ|συναδ|τσαμ|υποδ|φιλον|φυλοδ|χασ)$"
        if re.search(reCur, w) or re.search(exept5, w, re.U):
            w += "ικ";

    #Step 5
    re1 = "^(.+?)(αμε)$"
    re2 = "^(.+?)(αγαμε|ησαμε|ουσαμε|ηκαμε|ηθηκαμε)$"
    re3 = "^(.+?)(ανε)$"
    re4 = "^(.+?)(αγανε|ησανε|ουσανε|ιοντανε|ιοτανε|ιουντανε|οντανε|οτανε|ουντανε|ηκανε|ηθηκανε)$"
    re5 = "^(.+?)(ετε)$"
    re6 = "^(.+?)(ησετε)$"
    re7 = "^(.+?)(οντασ|ωντασ)$"
    re8 = "^(.+?)(ομαστε|ιομαστε)$"
    re9 = "^(.+?)(εστε)$"
    re10 = "^(.+?)(ιεστε)$"
    re11 = "^(.+?)(ηκα|ηκεσ|ηκε)$"
    re12 = "^(.+?)(ηθηκα|ηθηκεσ|ηθηκε)$"
    re13 = "^(.+?)(ουσα|ουσεσ|ουσε)$"
    re14 = "^(.+?)(αγα|αγεσ|αγε)$"
    re15 = "^(.+?)(ησε|ησου|ησα)$"
    re16 = "^(.+?)(ηστε)$"
    re17 = "^(.+?)(ουνε|ησουνε|ηθουνε)$"
    re18 = "^(.+?)(ουμε|ησουμε|ηθουμε)$"

    if(w == "αγαμε"):
        return "αγαμ"

    RegularExpr = re.compile(re2, re.U)
    Matches = RegularExpr.search(w)
    if Matches: #Step 5A
        stem = Matches.group(1)
        w = stem
        test1 = False
    else:
        RegularExpr = re.compile(re1, re.U)
        Matches = RegularExpr.search(w)
        if Matches:
            stem = Matches.group(1)
            w = stem
            test1 = False
            exept6 = "^(αναπ|αποθ|αποκ|αποστ|βουβ|ξεθ|ουλ|πεθ|πικρ|ποτ|σιχ|χ)$"
            if re.search(exept6, w, re.U):
                w += "αμ"
        else:
            RegularExpr = re.compile(re4, re.U)
            Matches = RegularExpr.search(w)
            if Matches: #Step 5B
                stem = Matches.group(1)
                w = stem
                test1 = False
                re4 = "^(τρ|τσ)$"
                if re.search(re4, w, re.U):
                    w += "αγαν"
            else:
                RegularExpr = re.compile(re3, re.U)
                Matches = RegularExpr.search(w)
                if Matches:
                    stem = Matches.group(1)
                    w = stem
                    test1 = False
                    re3 = "" + v2 + "$"
                    except7 = "^(βετερ|βουλκ|βραχμ|γ|δραδουμ|θ|καλπουζ|καστελ|κορμορ|λαοπλ|μωαμεθ|μ|μουσουλμ|ν|ουλ|π|πελεκ|πλ|πολισ|πορτολ|σαρακατσ|σουλτ|τσαρλατ|ορφ|τσιγγ|τσοπ|φωτοστεφ|χ|ψυχοπλ|αγ|ορφ|γαλ|γερ|δεκ|διπλ|αμερικαν|ουρ|πιθ|πουριτ|σ|ζωντ|ικ|καστ|κοπ|λιχ|λουθηρ|μαιντ|μελ|σιγ|σπ|στεγ|τραγ|τσαγ|φ|ερ|αδαπ|αθιγγ|αμηχ|ανικ|ανοργ|απηγ|απιθ|ατσιγγ|βασ|βασκ|βαθυγαλ|βιομηχ|βραχυκ|διατ|διαφ|ενοργ|θυσ|καπνοβιομηχ|καταγαλ|κλιβ|κοιλαρφ|λιβ|μεγλοβιομηχ|μικροβιομηχ|νταβ|ξηροκλιβ|ολιγοδαμ|ολογαλ|πενταρφ|περηφ|περιτρ|πλατ|πολυδαπ|πολυμηχ|στεφ|ταβ|τετ|υπερηφ|υποκοπ|χαμηλοδαπ|ψηλοταβ)$"
                    if (re.search(re3, w) or re.search(except7, w)):
                        w += "αν"
                else:
                    RegularExpr = re.compile(re6, re.U)
                    Matches = RegularExpr.search(w)
                    if Matches: #Step 5C
                        stem = Matches.group(1)
                        w = stem
                        test1 = False
                    else:
                        RegularExpr = re.compile(re5, re.U)
                        Matches = RegularExpr.search(w)
                        if Matches:
                            stem = Matches.group(1)
                            w = stem
                            test1 = False
                            re5 = v2
                            except8 = "(οδ|αιρ|φορ|ταθ|διαθ|σχ|ενδ|ευρ|τιθ|υπερθ|ραθ|ενθ|ροθ|σθ|πυρ|αιν|συνδ|συν|συνθ|χωρ|πον|βρ|καθ|ευθ|εκθ|νετ|ρον|αρκ|βαρ|βολ|ωφελ)$"
                            except9 = "^(αβαρ|βεν|εναρ|αβρ|αδ|αθ|αν|απλ|βαρον|ντρ|σκ|κοπ|μπορ|νιφ|παγ|παρακαλ|σερπ|σκελ|συρφ|τοκ|υ|δ|εμ|θαρρ|θ)$"
                            if re.search(re5, w, re.U) or re.search(except8, w, re.U):
                                w += "ετ"
                            elif re.search(except9, w, re.U):
                                w += "ετ"
                        else:
                            RegularExpr = re.compile(re7, re.U)
                            Matches = RegularExpr.search(w)
                            if Matches: #Step 5D
                                stem = Matches.group(1)
                                w = stem
                                test1 = False
                                except10 = "^(αρχ)$"
                                except11 = "(κρε)$"
                                if re.search(except10, w, re.U):
                                    w += "οντ"
                                if re.search(except11, w, re.U):
                                    w += "ωντ"
                            else:
                                RegularExpr = re.compile(re8, re.U)
                                Matches = RegularExpr.search(w)
                                if Matches: #Step 5E
                                    stem = Matches.group(1)
                                    w = stem
                                    test1 = False
                                    except11 = "^(ον)$"
                                    if re.search(except11, w, re.U):
                                        w += "ομαστ"
                                else:
                                    RegularExpr = re.compile(re10, re.U)
                                    Matches = RegularExpr.search(w)
                                    if Matches: #step 5F
                                        stem = Matches.group(1)
                                        w = stem
                                        test1 = False
                                        re10 = "^(π|απ|συμπ|ασυμπ|ακαταπ|αμεταμφ)$"
                                        if re.search(re10, w, re.U):
                                            w += "ιεστ"
                                    else:
                                        RegularExpr = re.compile(re9, re.U)
                                        Matches = RegularExpr.search(w)
                                        if Matches:
                                            stem = Matches.group(1)
                                            w = stem
                                            test1 = False
                                            except12 = "^(αλ|αρ|εκτελ|ζ|μ|ξ|παρακαλ|αρ|προ|νισ)$"
                                            if re.search(except12, w, re.U):
                                                w += "εστ"
                                        else:
                                            RegularExpr = re.compile(re12, re.U)
                                            Matches = RegularExpr.search(w)
                                            if Matches: #Step 5G
                                                stem = Matches.group(1)
                                                w = stem
                                                test1 = False
                                            else:
                                                RegularExpr = re.compile(re11, re.U)
                                                Matches = RegularExpr.search(w)
                                                if Matches:
                                                    stem = Matches.group(1)
                                                    w = stem
                                                    test1 = False
                                                    except13 = "(σκωλ|σκουλ|ναρθ|σφ|οθ|πιθ)$"
                                                    except14 = "^(διαθ|θ|παρακαταθ|προσθ|συνθ|)$"
                                                    if re.search(except13, w, re.U):
                                                        w += "ηκ"
                                                    elif re.search(except14, w, re.U):
                                                        w += "ηκ"
                                                else:
                                                    RegularExpr = re.compile(re13, re.U)
                                                    Matches = RegularExpr.search(w)
                                                    if Matches: #Step 5H
                                                        stem = Matches.group(1)
                                                        w = stem
                                                        test1 = False
                                                        except15 = "^(φαρμακ|χαδ|αγκ|αναρρ|βρομ|εκλιπ|λαμπιδ|λεχ|μ|πατ|ρ|λ|μεδ|μεσαζ|υποτειν|αμ|αιθ|ανηκ|δεσποζ|ενδιαφερ|δε|δευτερευ|καθαρευ|πλε|τσα)$"
                                                        except16 = "(ποδαρ|βλεπ|πανταχ|φρυδ|μαντιλ|μαλλ|κυματ|λαχ|ληγ|φαγ|ομ|πρωτ)$"
                                                        if re.search(except15, w, re.U):
                                                            w += "ουσ"
                                                        elif re.search(except16, w, re.U):
                                                            w += "ουσ"
                                                    else:
                                                        RegularExpr = re.compile(re14, re.U)
                                                        Matches = RegularExpr.search(w)
                                                        if Matches: #Step 5I
                                                            stem = Matches.group(1)
                                                            w = stem
                                                            test1 = False
                                                            except17 = "^(ψοφ|ναυλοχ)$"
                                                            except18 = "^(αβαστ|πολυφ|αδηφ|παμφ|ρ|ασπ|αφ|αμαλ|αμαλλι|ανυστ|απερ|ασπαρ|αχαρ|δερβεν|δροσοπ|ξεφ|νεοπ|νομοτ|ολοπ|ομοτ|προστ|προσωποπ|συμπ|συντ|τ|υποτ|χαρ|αειπ|αιμοστ|ανυπ|αποτ|αρτιπ|διατ|εν|επιτ|κροκαλοπ|σιδηροπ|λ|ναυ|ουλαμ|ουρ|π|τρ|μ)$"
                                                            except19 = "(οφ|πελ|χορτ|λλ|σφ|ρπ|φρ|πρ|λοχ|σμην)$"
                                                            except20 = "(κολλ)$"
                                                            if (re.search(except18, w, re.U) or re.search(except19, w, re.U)) and (re.search(except17, w, re.U) or re.search(except20, w, re.U)) :
                                                                w += "αγ"
                                                        else:
                                                            RegularExpr = re.compile(re15, re.U)
                                                            Matches = RegularExpr.search(w)
                                                            if Matches: #Step 5J
                                                                stem = Matches.group(1)
                                                                w = stem
                                                                test1 = False
                                                                except21 = "^(ν|χερσον|δωδεκαν|ερημον|μεγαλον|επταν)$"
                                                                if re.search(except21, w, re.U):
                                                                    w += "ησ"
                                                            else:
                                                                RegularExpr = re.compile(re16, re.U)
                                                                Matches = RegularExpr.search(w)
                                                                if Matches: #Step 5K
                                                                    stem = Matches.group(1)
                                                                    w = stem
                                                                    test1 = False
                                                                    except22 = "^(ασβ|σβ|αχρ|χρ|απλ|αειμν|δυσχρ|ευχρ|κοινοχρ|παλιμψ)$"
                                                                    if re.search(except22, w, re.U):
                                                                        w += "ηστ"
                                                                else:
                                                                    RegularExpr = re.compile(re17, re.U)
                                                                    Matches = RegularExpr.search(w)
                                                                    if Matches: #Step 5L
                                                                        stem = Matches.group(1)
                                                                        w = stem
                                                                        test1 = False
                                                                        except23 = "^(ν|ρ|σπι|στραβομουτσ|κακομουτσ|εξων)$"
                                                                        if re.search(except23, w, re.U):
                                                                            w += "ουν"
                                                                    else:
                                                                        RegularExpr = re.compile(re18, re.U)
                                                                        Matches = RegularExpr.search(w)
                                                                        if Matches: #Step 5M
                                                                            stem = Matches.group(1)
                                                                            w = stem
                                                                            test1 = False
                                                                            except24 = "^(παρασουσ|φ|χ|ωριοπλ|αζ|αλλοσουσ|ασουσ)$"
                                                                            if re.search(except24, w, re.U):
                                                                                w += "ουμ"

    #Step 6
    re1 = "^(.+?)(ματα|ματων|ματοσ)$"
    re2 = "^(.+?)(α|αγατε|αγαν|αει|αμαι|αν|ασ|ασαι|αται|αω|ε|ει|εισ|ειτε|εσαι|εσ|εται|ι|ιεμαι|ιεμαστε|ιεται|ιεσαι|ιεσαστε|ιομασταν|ιομουν|ιομουνα|ιονταν|ιοντουσαν|ιοσασταν|ιοσαστε|ιοσουν|ιοσουνα|ιοταν|ιουμα|ιουμαστε|ιουνται|ιουνταν|η|ηδεσ|ηδων|ηθει|ηθεισ|ηθειτε|ηθηκατε|ηθηκαν|ηθουν|ηθω|ηκατε|ηκαν|ησ|ησαν|ησατε|ησει|ησεσ|ησουν|ησω|ο|οι|ομαι|ομασταν|ομουν|ομουνα|ονται|ονταν|οντουσαν|οσ|οσασταν|οσαστε|οσουν|οσουνα|οταν|ου|ουμαι|ουμαστε|ουν|ουνται|ουνταν|ουσ|ουσαν|ουσατε|υ|υσ|ω|ων)$"

    RegularExpr = re.compile(re1, re.U)
    Matches = RegularExpr.search(w)
    if Matches:
        stem = Matches.group(1)
        w = stem + "μα"

    RegularExpr = re.compile(re2, re.U)
    Matches = RegularExpr.search(w)
    if (Matches and test1):
        stem = Matches.group(1)
        w = stem

    #Step 7
    re1 = "^(.+?)(εστερ|εστατ|οτερ|οτατ|υτερ|υτατ|ωτερ|ωτατ)$"

    RegularExpr = re.compile(re1, re.U)
    Matches = RegularExpr.search(w)
    if Matches:
        stem = Matches.group(1)
        w = stem

    return w

#endregion

#region Main

#region Checking if there already are data in the DB
if EventsEdges_coll.count() > 0:
    print("There's already data on the Events_Edges collection!!")
    pause_exit(status=0, message='Press any key to exit...')
if UsersEdges_coll.count() > 0:
    print("There's already data on the Users_Edges collection!!")
    pause_exit(status=0, message='Press any key to exit...')
if ProcessedTweets_coll.count() > 0:
    print("There's already data on the Processed_Tweet collection!!")
    pause_exit(status=0, message='Press any key to exit...')
if HashtagsEdges_coll.count() > 0:
    print("There's already data on the Hashtags_Edges collection!!")
    pause_exit(status=0, message='Press any key to exit...')
#endregion

try:
    curIndex = 0
    #region PreProcess
    #Pre-process for remove the hashtag we searched for from Edges_Hashtag
    HashtagSearcingFor = lstTrackingFor
    HashtagSearcingFor += "#iran"
    for i in range(0, len(HashtagSearcingFor)):
        HashtagSearcingFor[i] = HashtagSearcingFor[i].replace(" ", "").lower()
        if HashtagSearcingFor[i][:1] != "#":
            HashtagSearcingFor[i] = "#" + HashtagSearcingFor[i]
    HashtagSearcingFor = list(set(HashtagSearcingFor))

    #Pre-process for remove the hashtag we searched for from Edges_Events
    SearchingForProc = lstTrackingFor
    for i in range(0, len(SearchingForProc)):
        SearchingForProc[i] = SearchingForProc[i].lower()
        if SearchingForProc[i][:1] == "#":
            SearchingForProc[i] = SearchingForProc[i][1:]
    SearchingForText = " ".join([word for word in SearchingForProc])
    SearchingForText = removeSpecialCharsFromText(SearchingForText)

    #stemming
    SearchForList = SearchingForText.split(' ')
    CleanWordList = list()
    for word in SearchForList:
        CleanWordList.append(word)
    SingleStem = [stemmer.stem(stemTweet) for stemTweet in CleanWordList]
    StemString = ''
    for word in SingleStem:
        StemString += word + ' '
    stem_SearchFor = StemString.strip()
    #endregion

    for RawTweet in RawTweetsJSON_coll.find():
        #region InfoAcquisition
		#Acquiring basic info from the Raw Twitter JSON
        tweet_id = str(RawTweet["id_str"]).lower()
        user_id = str(RawTweet["user"]["id_str"]).lower()
        user_screenname = "@" + str(RawTweet["user"]["screen_name"]).lower()
        created_at = str(RawTweet["created_at"]).lower()
        timestamp_ms = str(RawTweet["timestamp_ms"]).lower()
        in_reply_to_status_id_str = str(RawTweet["in_reply_to_status_id_str"]).lower()
        in_reply_to_user_id_str = str(RawTweet["in_reply_to_user_id_str"]).lower()
        in_reply_to_screen_name = str(RawTweet["in_reply_to_screen_name"]).lower()
        friends_count = str(RawTweet["user"]["friends_count"]).lower()
        followers_count = str(RawTweet["user"]["followers_count"]).lower()
        statuses_count = str(RawTweet["user"]["statuses_count"]).lower()
        orig_tweet = str(RawTweet["text"]).lower()

        tempURLs = RawTweet["entities"]["urls"]
        urls = [None] * len(tempURLs)
        for i in range(0, len(tempURLs)):
            urls[i] = tempURLs[i]["expanded_url"].lower()

        temphashtags = RawTweet["entities"]["hashtags"]
        hashtags = [None] * len(temphashtags)
        for i in range(0, len(temphashtags)):
            hashtags[i] = temphashtags[i]["text"].lower()

        tempuser_mentions = RawTweet["entities"]["user_mentions"]
        user_mentions = [None] * len(tempuser_mentions)
        for i in range(0, len(tempuser_mentions)):
            user_mentions[i] = tempuser_mentions[i]["screen_name"].lower()

        for i in range(0, len(hashtags)):
            hashtags[i] = "#" + hashtags[i]

        for i in range(0, len(user_mentions)):
            user_mentions[i] = "@" + user_mentions[i]
        #endregion

        #region PreProcessing
		#Cleaning & Extrapolation data
        tweet_lowercase = orig_tweet.lower()
        tweet_lowercaseList = tweet_lowercase.split(" ")

        CleanURLs = getWordsStartingWith(tweet_lowercaseList, "http:")
        CleanURLs += getWordsStartingWith(tweet_lowercaseList, "https:")

        tweet_cleaned = removeListItemsFromText(tweet_lowercase, "rt ")
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, hashtags)
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, CleanURLs)
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, user_mentions)
        possibleuser_mentions = [None] * len(user_mentions)
        for i in range(0, len(user_mentions)):
            possibleuser_mentions[i] = user_mentions[i] + ":"
        tweet_cleaned = removeListItemsFromText(tweet_cleaned, possibleuser_mentions)
        #endregion

        #region NLP
        tweet_cleaned = removeSpecialCharsFromText(tweet_cleaned)
        #tweet_cleaned = normaliseText(tweet_cleaned) #For Greek tweets only
        tweet_cleaned = removeStopwords(tweet_cleaned, stopwords.words("english")) #, Greek_Stopwords)
        #tweet_cleaned = replace_all(tweet_cleaned, Step1List) #For Greek tweets only
        tweet_cleaned = tweet_cleaned.strip()
        #tweet_cleaned = StemAll(tweet_cleaned) #For Greek tweets only
        proc_tweet = tweet_cleaned
        #endregion

        #region Stemming
        #For English tweets only
        textList = proc_tweet.split(' ')
        cleanWords = list()
        for word in textList:
            cleanWords.append(word)
        singles = [stemmer.stem(stemTweet) for stemTweet in cleanWords]
        stemmedString = ''

        for word in singles:
            stemmedString += word + ' '

        stemmed_tweet = stemmedString.strip()
        #endregion

        #region Extrapolating URLS/Hashtags/Mentions/Entities
        strURLs = ' '.join([word for word in urls])
        strhashtags = ' '.join([word for word in hashtags])
        struser_mentions = ' '.join([word for word in user_mentions])
        #namedEntities = getTheNamedEntities(orig_tweet)
        #endregion

        #region Data Processing for saving
        to_SpaceSeparated = stemmed_tweet
        if len(urls) > 0:
            to_SpaceSeparated = strURLs + " " + to_SpaceSeparated
        if len(hashtags) > 0:
            to_SpaceSeparated = strhashtags + " " + to_SpaceSeparated
        if len(user_mentions) > 0:
            to_SpaceSeparated = struser_mentions + " " + to_SpaceSeparated

        #Getting the Processed Data JSON ready to be inserted into the MongoDB
        proc_data = {
                    "Gephi_Data": {
                        "from": user_screenname,
                        "to_SpaceSeparated": to_SpaceSeparated
                        },
                    "username": user_screenname,
                    "user_id": user_id,
                    "tweet_id": tweet_id,
                    "created_at": created_at,
                    "timestamp_ms": timestamp_ms,
                    "in_reply_to_status_id_str": in_reply_to_status_id_str,
                    "in_reply_to_user_id_str": in_reply_to_user_id_str,
                    "in_reply_to_screen_name": in_reply_to_screen_name,
                    "friends_count": friends_count,
                    "followers_count": followers_count,
                    "statuses_count": statuses_count,
                    "urls": urls,
                    "hashtags": hashtags,
                    "user_mantions": user_mentions,
                    "proc_tweet": proc_tweet,
                    "stemmed_tweet": stemmed_tweet
                    }

        #Getting the Events Edges List ready to be iterated upon and inserted into the MongoDB
        to_Events_OneByOne = removeListItemsFromText(stemmed_tweet, stem_SearchFor.split(' '))
        to_Events_OneByOne = to_Events_OneByOne.split(" ")
        #Used ONLY if URLS and Hashtags are to be inserted into the Events
        #if len(urls) > 0:
        #    for i in range(0, len(urls)):
        #        to_Events_OneByOne.append(urls[i])
        #if len(hashtags) > 0:
        #    for i in range(0, len(hashtags)):
        #        to_Events_OneByOne.append(hashtags[i])
        #endregion

        #region Saving the Data
        #Inserting them to the MongoDB database

        #Saving Collection hashtags Edges
        if len(hashtags) > 0:
            ValidHashtags = " ".join([word for word in hashtags if word.lower() not in HashtagSearcingFor])
            ValidHashtags = removeListItemsFromText(ValidHashtags, SearchForList)
            ValidHashtags = ValidHashtags.split(" ")
            for i in range(0, len(ValidHashtags)):
                HashtagsEdges_coll.insert_one({"from": user_screenname, "to": ValidHashtags[i], "tweet_id": tweet_id, "orig_tweet": orig_tweet})

        #Saving Collection Processed Tweet
        mongo_proc_data = ProcessedTweets_coll.insert_one(proc_data)

        #Saving Collection User Edges
        if len(user_mentions) > 0:
            for i in range(0, len(user_mentions)):
                UsersEdges_coll.insert_one({"from": user_screenname, "to": user_mentions[i], "tweet_id": tweet_id, "orig_tweet": orig_tweet})

        #Saving Collection Events Edges
        if len(to_Events_OneByOne) > 0:
            for i in range(0, len(to_Events_OneByOne)):
                EventsEdges_coll.insert_one({"from": user_screenname, "to": to_Events_OneByOne[i], "tweet_id": tweet_id, "orig_tweet": orig_tweet})
        #endregion

        try:
            curIndex += 1
            print(curIndex)
        except Exception as ex:
            print('Print error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(ex) + '\n')
            continue

    print("The programme has finished!")

except Exception as e:
    eMessage = 'Main error\n' + 'Time of Error: ' + str(datetime.now()) + '\n' + str(e) + '\n'
    print (str(eMessage))
    saveFile = open(Current_Path + 'TweetProcessing_Problems.txt', 'a')
    saveFile.write(eMessage)
    saveFile.close()
#endregion