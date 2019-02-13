#This file is 

# import requests to fetch the website (there are many ways of doing this)
import requests
# import scrapy to develop the Selectors that extract the data we want, to prove they work
import scrapy
# we import scrapy.selector as Selector and remove_tags for use later
from scrapy.selector import Selector
from scrapy.utils.markup import remove_tags


class Thread:
    def __init__(self):
        self.title = None
        self.posts = []
        self.url = None
        self.op_account_name = None

def extract_thread_data(html_text):
    new_thread = Thread()
    new_thread.title = Selector(text = html_text).xpath("//h2[@class='topic-title']/a/text()").extract()[0]
    new_thread.url = thread_url
    return new_thread

class Post:
    def __init__(self):
        self.user = None
        self.title = None
        self.content = None
    
def extract_post_data(html_text):
    post_titles = Selector(text = html_text).xpath("//div[@class='postbody']//h3/a/text()").extract()
    post_users = Selector(text = html_text).xpath("//div[@class='postbody']//span[@class='username']/text()").extract()
    post_contents = Selector(text = html_text).xpath("//div[@class='postbody']//div[@class='content']").extract()
    posts = []
    for title, author, content in zip(post_titles, post_users, post_contents):
        new_post = Post()
        new_post.user = author
        new_post.title = title
        new_post.content = ''.join(remove_tags(content)) #We use join here as content is a list, which we want to flatten into a string
        posts.append(new_post)
    return posts

def scrape_thread(html_text):
    thread = extract_thread_data(html_text)
    thread.posts = extract_post_data(html_text)
    thread.op_account_name = thread.posts[0].user
    return thread

#Yes I know I should be modifying the thread __str__ and __repr__, #streach goals.
def print_thread(thread):
    print("Thread title:", thread.title)
    print("Thread url:", thread.url)
    print("Thread op_account_name:", thread.op_account_name)
    print("Posts:")
    for post in thread.posts:
        print("\nPost title:", post.title)
        print("Post user:", post.user)
        print("Post content:")
        print("''\n",post.content,"\n''")


thread_url = "https://learningautomaton.ca/wp-content/uploads/2019/02/FruitsAndVeggiesForum/Bears.%20Beets.%20-%20Fruits%20and%20Veggies.html"
request_file = requests.get(thread_url)
thread_html_text = request_file.text
thread = scrape_thread(thread_html_text)
print_thread(thread)