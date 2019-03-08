import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.utils.markup import remove_tags
from scrapy.spiders import CrawlSpider, Rule
import datetime

#Fruits and Veggies spider, for crawling the mock fruitsandveggies forum, hosted on learningautomaton.ca
class FVSpider(CrawlSpider):
    
    # setting the name of the Spider, which we will use to run the Spider from Scrapy in our shell
    name = 'fruitsandveggies'
    # explicitly allowing learningautomaton.ca only
    allowed_domains = ['learningautomaton.ca']
    # setting the url to start from, in this case the home page of our forum
    start_urls = ['https://learningautomaton.ca/wp-content/uploads/2019/02/FruitsAndVeggiesForum/Fruits%20and%20Veggies%20-%20Index%20page.html']
    
    # making our link extractors, run on each webpage we start on or follow to, to extract links for the CrawlSpider rules
    # extracts links to take us from forum home page into the forums
    forum_link_extractor = LinkExtractor(restrict_xpaths = "//a[@class='forumtitle']")
    # extracts links to take us from the forum pages into the threads
    thread_link_extractor = LinkExtractor(restrict_xpaths= "//a[@class='topictitle']")
    # extract links to take us from the thread first page to follow on pages of the same thread
    nextpage_link_extractor = LinkExtractor(restrict_xpaths= "//a[@rel='next']")

    # the rules that tell CrawlSpider what links to follow (i.e. run the rules again on to get more links) 
    # and what pages to pass to the callback function for parsing data from
    rules = (
        Rule(forum_link_extractor, follow=True), # follow links to boards, and extract links as per rules
        Rule(thread_link_extractor, follow=True, callback = 'parse_post_data'), # follow links to forums, extract links as per rules, parse for post and thread info
        Rule(nextpage_link_extractor, follow=True, callback = 'parse_post_data') # follow links to next pages, extract links as per rules, parse for post and thread info
    )

    # function called for every thread page and thread next page, is passed a Scrapy response object containing the page info
    def parse_post_data(self, response):
        
        # Thread class to hold our thread data, subclassing scrapy.Item for ease of use and storing into our DB
        class Thread(scrapy.Item):
            title = scrapy.Field()
            url = scrapy.Field()
            posts = scrapy.Field()
            op_account_name = scrapy.Field()

        # Post class to hold individual posts, subclassing same as the Thread class
        class Post(scrapy.Item):
            user = scrapy.Field()
            title = scrapy.Field()
            content = scrapy.Field()
            datetime = scrapy.Field()

        # extracts info on the thread its self, returns a Thread instance with the data
        def extract_thread_data(response):
            new_thread = Thread()
            new_thread['title'] = response.xpath("//h2[@class='topic-title']/a/text()").extract()[0]
            new_thread['url'] = response.url
            return new_thread

        # extracts post data for all posts on a page, returns a list of Post instances with the data
        def extract_post_data(response):
            # the xpath.extract() function returns a list of all instances that match the xpath string. 
            # i.e. post_titles will be a list of all post titles in the order encountered, post_users will be all users in the order encountered, etc
            post_titles = response.xpath("//div[@class='postbody']//h3/a/text()").extract()
            post_users = response.xpath("//div[@class='postbody']//span[@class='username']/text()").extract()
            post_contents = response.xpath("//div[@class='postbody']//div[@class='content']").extract()
            post_datestrings = response.xpath("//div[@class='postbody']//p[@class='author']/text()[3]").extract()
            
            # zip the lists togeather, and for each set make a new Post object and add it to a list, return the list
            posts = []
            for title, author, content, datestring in zip(post_titles, post_users, post_contents, post_datestrings):
                new_post = Post()
                new_post['user'] = author
                new_post['title'] = title
                new_post['content'] = ''.join(remove_tags(content)) # we use join here as content for each post is a list, which we want to flatten into a string
                # clean the date string: "Wed Feb 06, 2019 12:37 am" => "WedFeb0620191237am"
                datestring = datestring.replace("\n","").replace("\t","").replace(" ","").replace(":","").replace(",","") 
                # create a date time object from the cleaned string using the strptime format string: 
                # %a:day(Wed), %b:month(Feb), %d:day(06), %Y:year(2019), %M:12h time(1237), %p:am/pm(am) 
                dt = datetime.datetime.strptime(datestring,"%a%b%d%Y%I%M%p")
                new_post['datetime'] = dt
                posts.append(new_post)
            return posts

        thread = extract_thread_data(response)
        thread['posts'] = extract_post_data(response)
        # because the thread itsself does not store the original poster (OP, aka thread starter), we pull the user name from the first post as the OP.
        thread['op_account_name'] = thread['posts'][0]['user']
        return thread

