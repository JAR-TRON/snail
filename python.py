# -------------------------
#   Importing libraries
# -------------------------
import os
from selenium import webdriver
import pandas as pd
import time
from bs4 import BeautifulSoup
import warnings
from ktrain import text
warnings.filterwarnings("ignore")

# -------------------------
#    Classes nd Objects
# -------------------------
class Classifier:
    '''
    ## Introduction
    Creates a zero shot classifier under Ktrain that uses Natural
    Language Inference(NLI) to predict the senses of the sentence/
    word/token.
    
    Probabilistic model that doesn't requires model training and 
    predictions can be made directly calling `predict` method.
    
    It'll be called if there is the requirement of predicting 
    label of any sentence during web crawling.
    
    ## Example:
    ```python
    >> labels = ["Laptops", "Review", "Price"]
    >> classifier = Classifier(labels)  # Initialize the classifier
    >> doc = "XYZ Laptop Name"
    >> classifier.predict(doc)  # Returns the label that has highest probability
    Output: (Laptops, probability[float])
    ```
    '''
    def __init__(self, labels) -> None:
        
        print('Intializing the zero shot classifier')
        print('It might take some time to execute!!')
        self.zsl = text.ZeroShotClassifier()
        self.labels = labels
        print('Classifier is initialized!!')
        print()
    
    def predict(self, doc):
        '''
        Make prediction on ZSl classifier
        '''
        prediction = self.zsl.predict(doc, labels=self.labels, include_labels=True)
        probability = 0
        label = ''
        
        # Traverse into `prediction` list to give the 
        ## label that has highest probability among all
        ## of the other labels.
        for i in range(len(prediction)):
            temp = prediction[i]
            if temp[1] > probability:
                probability = temp[1]
                label = temp[0]
        
        return (label, probability)

class Crawler:
    '''
    ### Introduction
    Crawler is used to crawl into the different websites and 
    performes some basic functionalities.
    
    ### Functionalities
    [1]. Made google search. \n
    [2]. Fetch all of the links after a google search. \n
    [3]. Fetch all of the text of any(relevant) html tag in 
    a website. \n
    [4]. Fetch all of the html classes of any(relevant) html
    tag on a page. \n
    [5]. Get all of the tags that are being used in a website. \n
    '''
    def __init__(self, driver) -> None:
        self.driver = driver
    
    def make_google_search(self, keyword) -> None:
        '''
        Used to make a google search for the keyword entered
        '''
        self.driver.get(f'https://www.google.co.in/search?q={keyword}')
    
    def get_all_links(self) -> list:
        '''
        Used to fetch all the links of results shown after a
        google search. \n
        Return a list of all links
        '''
        
        # Content of html page
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        links = []
        
        # Fetch all links of results shown after google search
        for div in soup.findAll('div', attrs={'class': 'yuRUbf'}):
            address = div.find('a').get('href')
            links.append(address)
        return links
    
    def get_text(self, tag, attr={}):
        '''
        Returns text inside specified html `tag`.
        
        :param tag: A filter on tag name.
        :param attr: A dictionary of filters on attribute values.
        
        ## Example:
        ```python
        >>> div = "div"
        >>> attr = {"class": "xyz"}
        >>> crawler = Crawler(driver)
        >>> crawler.get_text(tag = div, attr = attr)
        Output: ['text_1', 'text_2', ...]
        ```
        '''
        assert tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'table',
                    'link', 'div', 'g', 'title', 'ul', 'form', 'button',
                    'b', 'span', 'a', 'head', 'body',
                    ]
        
        # Content of html page
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        tags = []
        
        for heading in soup.findAll(tag, attrs=attr):
            try:
                # Getting total number of words in a sentence.
                heading_len = len(heading.text.split(' '))
                
                # Getting text only if it has limit of 25 words.
                if heading_len <= 25:
                    tags.append(heading.text)
            except:
                pass
        
        # Ignore the group if number of sentence are less then 8.
        if 8 <= len(tags):
            # Ignore the group if it has higher number of
            ## repetitive tokens/words.
            check_return = True
            for i in range(len(tags)):
                if tags.count(tags[i]) < len(tags) // 2:
                    check_return = True
                else:
                    check_return = False
                    break
            
            if check_return:
                return tags
            else:
                return None
    
    def get_all_classes(self, tag):
        '''
        Returns a `set` of html classes of the specified tag.
        
        ## Example:
        >>> h1 = "h1"
        >>> crawler = Crawler(driver)
        >>> crawler.get_all_classes(tag = h1)
        Output: {"class_1", "class_2", ...}
        '''
        classes = set()
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        
        for elements in soup.find_all(tag, class_ = True):
            classes.update(elements['class'])
        
        return classes
    
    def get_all_tags(self):
        '''
        Returns all tags that are being used in a website.
        '''
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        
        return ({tags.name for tags in soup.find_all()}, soup)


class Starter:
    '''
    This class is a basic class used to take inputs of 
    task user want to perform
    '''
    def starter(self):
        '''
        Used to take initial task input
        '''
        input_task = int(input('''what you want to do today:-     \
                \n[1]. Search about something                     \
                \n[2]. Scrap data                                 \
                \n[3]. Entertainment                              \
            \n'''))
        assert input_task in [1, 2, 3]
        return input_task

    def pick_driver(self):
        '''
        Initialize and return the web driver
        '''
        driver = webdriver.Chrome("./snail/chromedriver.exe")
        return driver


class Scrapper:
    '''
    Perform all of the scrapping tasks.
    '''
    def __init__(self, driver) -> None:
        self.driver = driver
    
    def make_input(self):
        '''
        Take input of either website name or its url
        and accordingly go to the desired page.
        '''
        data_input = int(input('''\n[1]. Enter the website name    \
                                \n[2]. Enter the url               \
                                \n'''))
        assert data_input in [1, 2]
        
        # If url is entered then directly go to the specific url
        ## else first make a google search and go to the site that
        ## appears on the top of the result.
        if data_input == 2:
            url = input('Enter the url:- ')
            self.driver.get(url)
        else:
            website_name = input('Enter the website name:- ')
            crawler = Crawler(self.driver)
            crawler.make_google_search(website_name)
            links = crawler.get_all_links()
            if f'https://www.{website_name}' in links[0]:
                self.driver.get(links[0])
    
    def ask_again(self):
        '''
        Used after `make_input` method to choose one of 
        the options scrap data or search any item.
        '''
        data_input = int(input('''\n[1]. Scrap the data here    \
                                \n[2]. Make a search here       \
                                \n'''))
        assert data_input in [1, 2]
        
        if data_input == 1:
            # scrap the data here
            self.scrapper()
        else:
            # make the search on this site
            current_url = self.driver.current_url
            search = input("Search anything:-  ")
            if current_url[-1] == '/':
                new_url = current_url + "search?q=" + search
            else:
                new_url = current_url + "/search?q=" + search
            self.driver.get(new_url)
            self.ask_again()
    
    def scrapper(self):
        crawler = Crawler(self.driver)
        tags = crawler.get_all_classes(tag='div')    # get all classes
        data = dict()
        
        specs = input("Enter the names to search:  ").split(' ')
        classifier = Classifier(specs)
        for pucha in tags:
            text = crawler.get_text('div', attr={'class': pucha})
            if text:
                # print(text)
                prediction = classifier.predict(text[0])
                print(prediction)
                if prediction[1] >= 0.20:
                    # print('hello')
                    pred = data.get(prediction[0], None)
                    if pred is None:
                        data[prediction[0]] = [text, 1, len(text)]
                    else:
                        name = prediction[0] + '-' + str(pred[1])
                        data[name] = [text, 1, len(text)]
                        data[prediction[0]][1] = pred[1] + 1
        
        max_len = 0
        for i in data.values():
            text_length = i[2]
            if text_length > max_len:
                max_len = text_length
        
        for key, value in data.items():
            print(key)
            text_length = value[2]
            text_ls = value[0]
            for i in range(text_length, max_len):
                text_ls.append('')
            data[key] = text_ls
        
        df = pd.DataFrame(data)
        print(df.head(10))
        df.to_csv('Title.csv')


# -------------------------------
#     Object initialization
# -------------------------------
starter = Starter().starter()
driver = Starter().pick_driver()

if starter == 2:
    scrapper = Scrapper(driver)
    scrapper.make_input()
    scrapper.ask_again()
    time.sleep(10)
    driver.close()


# -------------------------------
#     Extra testing purpose
# -------------------------------

# ask_again ------------>  add using previous url for searches
# filter search
# don't match spelling of website name to the url...?
# scrape data by id/class
# get me a valid class?


