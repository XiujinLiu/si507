import json
import requests
import webbrowser
import os.path
import matplotlib.pyplot as plt

# OMDB
my_key = "f9ba1464"

# plt
plt.style.use('_mpl-gallery')
# tree
GuessTree = \
    ("Do you want happy ending?",
        ("happy", None, None),
        ("sad", None, None))

# cache path
cache_path = cache_path = "C:/Users/liuxj/Desktop/cache.json"
cache_exist = 0
# question tree filepath
file_name = "C:/Users/liuxj/Desktop/tree_question.json"

class Video:
    def __init__(self, json):
        self.json = json
        self.type = json['Type']
        self.title=json['Title']
        self.year=json['Year']
        self.poster_url = json['Poster']
        self.genre = json['Genre']
        self.plot = json['Plot']
        self.IMDb = json["imdbID"]

    def info(self):
        return self.title+" at "+self.year+" with plot: "+ self.plot + "[" + self.genre + "]"

    def reach_poster(self):
        img = self.poster
        if self.poster_url != "N/A":
                webbrowser.open(img)
        else:
            print("No Poster Available")

    def get_clean_dictionary(self):
        clean_dictionary = {}
        for key in self.json.keys():
            if self.json[key] != 'N/A':
                clean_dictionary[key] = self.json[key]
        return clean_dictionary
    def tree(self):
        tree = \
            ("Do you want to check all information?",
                (self.get_clean_dictionary(), None, None),
                ("Do you want to check imdbID?",
                    (self.IMDb, None, None),
                    ("Do you want to check the plot?",
                        (self.plot, None, None),
                        ("Do you want to check poster?",
                            (self.poster_url, None, None),
                            (self.title, None, None)))))
        return tree

class Movie(Video):
    def __init__(self, json):
        super().__init__(json)
        if 'DVD' in json.keys():
            self.DVD = json['DVD']
        else:
            self.DVD = "N/A"
    def info(self):
        a = super().info()
        return a +" (DVD date"+ self.DVD + ")"
    

class Series(Video):
    def __init__(self, json):
        super().__init__(json)
        if 'totalSeasons' in json.keys():
            self.total_seasons = json['totalSeasons']
        else:
            self.total_seasons = "N/A"
    def info(self):
        a = super().info()
        return a+" (total seasons" + self.total_seasons + ")"

class Episode(Video):
    def __init__(self, json):
        super().__init__(json)
        if 'Season' in json.keys():
            self.season = json['Season']
        else:
            self.season = "N/A"
        if 'Episode'in json.keys():
            self.episode = json['Episode']
        else:
            self.episode = "N/A"
    def info(self):
        a = super().info()
        return a + " (season" + self.season + " episode" + self.episode + ")"

def parse_json(term):
    url_full = 'http://www.omdbapi.com/?s=' + term + '&apikey=' + my_key
    r = requests.get(url_full)
    search_json = json.loads(r.text)
    return search_json

def get_detail_json(result):
    imdb_id = result['imdbID']
    url_detail = 'http://www.omdbapi.com/?i=' + imdb_id + '&apikey=' + my_key
    get_detail_json = requests.get(url_detail)
    detail_json = json.loads(get_detail_json.text)
    return detail_json

def handle_result(term, json = None):
    """
    This function will get the data according to the search term
    and handle the data, including parse data, classify the data
    and return a tuple with differnt combination
    input: term: string
           json: list
    output: tuple
    """
    obj_list = []
    movie_list = []
    series_list = []
    episode_list = []
    if json == None:
        search_json = parse_json(term)
        if (search_json['Response'] == 'False'):
            print("The searching result is empty! \n")
            return False
        else:
            result_list = search_json['Search']
            result_movies = [x for x in result_list if x['Type']=='movie' ]
            result_serieses = [x for x in result_list if x['Type']=='series' ]
            result_episodes = [x for x in result_list if x['Type']=='episode' ]
            for result_movie in result_movies:
                detail_json = get_detail_json(result_movie)
                try:
                    obj_list.append(Video(detail_json))
                    movie_list.append(Movie(detail_json))
                except:
                    pass
            for result_series in result_serieses:
                detail_json = get_detail_json(result_series)
                try:
                    obj_list.append(Video(detail_json))
                    series_list.append(Series(detail_json))
                except:
                    pass
            for result_episode in result_episodes:
                detail_json = get_detail_json(result_episode)
                try:
                    obj_list.append(Video(detail_json))
                    episode_list.append(Episode(detail_json))
                except:
                    pass
    else:
        for i in json:
            for j in i:
                if term in i[j] or term.title() in i[j]:
                    obj_list.append(Video(i))
                    if i['Type'] == 'movie':
                        movie_list.append(Movie(i))
                    if i['Type'] == 'series':
                        series_list.append(Series(i))
                    if i['Type'] == 'episode':
                        episode_list.append(Episode(i))
        if obj_list == []:
            print("The searching result is empty in search history, we search on the website for you! \n")
            return handle_result(term)
    choose_type_tree = \
        ("Do you want to check all type?",
            (obj_list, None, None),
            ("Do you want to check movie type?",
                (movie_list, None, None),
                ("Do you want to check series type?",
                    (series_list, None, None),
                    (episode_list, None, None))))
    return choose_type_tree

def isLeaf(tree):
    node1, node2, node3 = tree
    if node2 == None and node3 == None:
        return True
    else:
        return False

def yes(prompt):
    question = prompt+" "
    while True:
        get_answer = input(question)
        get_answer.lower()
        if get_answer == "yes" or get_answer == "of course" or get_answer == "yup" or get_answer == "y" or get_answer == "sure" or get_answer == "true":
            return True
        elif get_answer == "no" or get_answer == 'n' or get_answer == "not" or get_answer == "nope" or get_answer == "false":
            return False
        else:
            print("Not a valid answer!")

def playLeaf(tree):
    """
    This function will process the data and display them, and also cache the data
    input: tuple
    output: boolean
    """
    Node1, Node2, Node3 = tree
    search_start = 0
    if os.path.exists(cache_path):
        if yes("Do you want we to guess from your search history? "):
            with open(cache_path, 'r') as f:
                c = f.read()
            cache = json.loads(c)
            choose_type_tree = handle_result(Node1, json = cache)
            search_start = 1
    if search_start == 0:
        choose_type_tree = handle_result(Node1)
    node1, node2, node3 = choose_type_tree
    print("We already know what is good for you.")
    recommend_json = []
    if yes(node1):
        node0_1, node0_2, node0_3 = node2
        recommend_json = node0_1
    else:
        node1_1, node1_2, node1_3 = node3
        if yes(node1_1):
            node0_11, node0_12, node0_13 = node1_2
            recommend_json = node0_11
        else:
            node2_1, node2_2, node2_3 = node1_3
            if yes(node2_1):
                node2_2_1, node2_2_2, node2_2_3 = node2_2
                recommend_json = node2_2_1
            else:
                node2_3_1, node2_3_2, node2_3_3 = node2_3
                recommend_json = node2_3_1
    
    count = 1
    for i in recommend_json:
        print(str(count) + ' ' + i.info())
        count += 1
    if yes("do you want to check year scatter graph"):
        x = []
        y = []
        for i in range(len(recommend_json)):
            year = recommend_json[i].year[0:4]
            x.append(i * 10)
            y.append(int(year)/2030 * len(recommend_json) * 10)
        plt.figure()
        plt.plot(x, y, 'o', markerfacecolor='purple')
        plt.show()
    favorite = []
    if yes("do you want more information of the one you like?"):
        while True:
            number = input("input the index of video. ")
            if number.isnumeric() == False or int(number) > len(recommend_json):
                print("please input a number in range")
            else:
                num_int=int(number)
                idx = num_int-1
                obj = recommend_json[idx]
                favorite = obj
                tree = favorite.tree()
                node1, node2, node3 = choose_type_tree = tree
                if yes(node1):
                    node0_1, node0_2, node0_3 = node2
                    print(node0_1)
                else:
                    node1_1, node1_2, node1_3 = node3
                    if yes(node1_1):
                        node0_11, node0_12, node0_13 = node1_2
                        print(node0_11)
                    else:
                        node2_1, node2_2, node2_3 = node1_3
                        if yes(node2_1):
                            node2_2_1, node2_2_2, node2_2_3 = node2_2
                            print(node2_2_1)
                        else:
                            node2_3_1, node2_3_2, node2_3_3 = node2_3
                            if yes(node2_3_1):
                                node2_3_2_1, node2_3_2_2, node2_3_2_3 = node2_3_2
                                webbrowser.open(node2_3_2_1)
                            else:
                                node2_3_3_1, node2_3_3_2, node2_3_3_3 = node2_3_3
                                print(node2_3_3_1)
                break
    if yes("Is the recommendation what you want?"):
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                c = f.read()
            cache = json.loads(c)
        else:
            cache = []
        for i in recommend_json:
            check_dupilicate = False
            for j in cache:
                if i.get_clean_dictionary() == j:
                    check_dupilicate = True
            if check_dupilicate == False:
                cache.append(i.get_clean_dictionary())
        write_in_file = json.dumps(cache)

        with open(cache_path,'w') as f:
            f.write(write_in_file)
        cache_exist = 1
        return True
    else:
        return False

def play(tree):
    """ This function will ask users to input yes or no and it will choose correct
    paths of the answer. If it is not correct, it will build a new tree based on the
    user's correct answer.

    Parameters
    ----------
    tree: tuple
        contains a question and two subtrees

    Returns
    -------
    tree: tuple
        a new tuple based on the answer

    """
    node1, node2, node3 = tree
    if isLeaf(tree):
        if playLeaf(tree):
            print("Enjoy it!")
            return tree
        else:
            answer = input("What is the key word you want? ")
            follow_question1 = input("What's a question that distinguishes between " + answer + " and " + node1 + "? ")
            if yes("and what's the answer for " + answer + "?"):
                return (follow_question1, (answer, None, None), tree)
            else:
                return (follow_question1, tree, (answer, None, None))
    else:
        if yes(node1):
            return (node1, play(node2), node3)
        else:
            return (node1, node2, play(node3))

def saveTree(tree,treefile) :
    node1, node2, node3 = tree
    if node2 == None and node3 == None:
        print("Leaf",file=treefile)
        print(node1,file=treefile)
    else:
        print("Internal node",file=treefile)
        print(node1,file=treefile)
        saveTree(node2,treefile)
        saveTree(node3,treefile)

def loadTree(treefile):
    idc = treefile.readline()
    content = treefile.readline()
    idc = idc.strip()
    content = content.strip()
    if idc == "Internal node":
        node1 = content
        return (node1,loadTree(treefile),loadTree(treefile))
    elif idc == "Leaf":
        return (content,None,None)

def main():
    print("Welcome to OMDb API!")
    if yes("Do you have a specific IMDb ID of the video?"):
        imdb_id = input("What's the IMDb ID of the video? ")
        url_detail = 'http://www.omdbapi.com/?i=' + imdb_id + '&apikey=' + my_key
        get_detail_json = requests.get(url_detail)
        detail_json = json.loads(get_detail_json.text)
        video = Video(detail_json)
        detail_dictionary = video.get_clean_dictionary()
        print(detail_dictionary)
    elif yes("Do you have a specific name of the video?"):
        video_name = str(input("What's the name of the video? "))
        url_detail = 'http://www.omdbapi.com/?t=' + video_name + '&apikey=' + my_key
        get_detail_json = requests.get(url_detail)
        detail_json = json.loads(get_detail_json.text)
        video = Video(detail_json)
        detail_dictionary = video.get_clean_dictionary()
        print(detail_dictionary)
    else:
        print('Let me guess what you like!')
        if yes("Would you like to load a tree a file with your preference?"):
            file_input = open(file_name, 'r')
            tree = loadTree(file_input)
            file_input.close()
        else:
            tree = GuessTree

        repeat = 1
        while repeat == 1:
            tree = play(tree)
            if yes("Would you like search again?"):
                repeat = 1
            else:
                repeat = 0
        if yes("Would you like to save this tree for later?"):
            file_path = open(file_name,"w")
            saveTree(tree,file_path)
            file_path.close()
            print("Thank you! The file has been saved.")
    print("Bye!")
main()
