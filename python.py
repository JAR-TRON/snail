from selenium import webdriver
import pandas as pd
import time
from bs4 import BeautifulSoup
import warnings
from ktrain import text
warnings.filterwarnings("ignore")

class Classifier:
    def __init__(self, labels) -> None:
        self.zsl = text.ZeroShotClassifier()
        self.labels = labels
    
    def predict(self, doc):
        prediction = self.zsl.predict(doc, labels=self.labels, include_labels=True)
        probability = 0
        label = ''
        
        for i in range(len(prediction)):
            temp = prediction[i]
            if temp[1] > probability:
                probability = temp[1]
                label = temp[0]
        
        return (label, probability)

class Crawler:
    def __init__(self, driver) -> None:
        self.driver = driver
    
    def make_google_search(self, keyword) -> None:
        '''
        Used to make a google search for the keyword entered
        '''
        self.driver.get(f'https://www.google.co.in/search?q={keyword}')
    
    def get_all_links(self) -> list:
        '''
        Used to fetch all the links shown after a google search
        i.e. links of websites of all results after a google search.
        
        Return a list of all links
        '''
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        links = []
        
        print('{', end='')
        for div in soup.findAll('div', attrs={'class': 'yuRUbf'}):
            address = div.find('a').get('href')
            print(f"'{address}',")
            links.append(address)
        print('}')
        return links
    
    def get_text(self, tag, attr={}):
        assert tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'table',
                    'link', 'div', 'g', 'title', 'ul', 'form', 'button',
                    'b', 'span', 'a', 'head', 'body',
                    ]
        
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        tags = []
        
        for heading in soup.findAll(tag, attrs=attr):
            try:
                heading_len = len(heading.text.split(' '))
                if heading_len <= 25:
                    # print(heading.text)
                    tags.append(heading.text)
            except:
                pass
        
        if 8 <= len(tags):
            if tags.count(tags[0]) != len(tags) // 2:
                return tags
    
    def get_all_classes(self, tags=None):
        classes = set()
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        
        for elements in soup.find_all(tags, class_ = True):
            classes.update(elements['class'])
        
        return classes
    
    def get_all_tags(self):
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        
        return ({tags.name for tags in soup.find_all()}, soup)
    
    def find_text(self, tag):
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        
        text = soup.select(tag).text
        return text

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
        Initialize and return the driver
        '''
        driver = webdriver.Chrome("./chromedriver")
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
        # tags = crawler.get_tags('a', attr={'class': '_3SkBxJ'})
        tags = crawler.get_all_classes(tags='div')                          # get all classes
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


