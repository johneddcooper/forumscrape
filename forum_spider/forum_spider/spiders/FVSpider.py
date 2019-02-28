import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.utils.markup import remove_tags
from scrapy.spiders import CrawlSpider, Rule
import datetime

class FVSpider(CrawlSpider):
    name = 'fruitsandveggies'
    allowed_domains = ['learningautomaton.ca']
    start_urls = ['https://learningautomaton.ca/wp-content/uploads/2019/02/FruitsAndVeggiesForum/Fruits%20and%20Veggies%20-%20Index%20page.html']
    
    forum_link_extractor = LinkExtractor(restrict_xpaths = "//a[@class='forumtitle']")
    thread_link_extractor = LinkExtractor(restrict_xpaths= "//a[@class='topictitle']")
    nextpage_link_extractor = LinkExtractor(restrict_xpaths= "//a[@rel='next']")

    rules = (
        Rule(forum_link_extractor, follow=True),
        Rule(thread_link_extractor, follow=True, callback = 'parse_post_data'),
        Rule(nextpage_link_extractor, callback = 'parse_post_data')
    )

    def parse_post_data(self, response):
#TODO, add next page logic to exract post data (?)
        class Thread(scrapy.Item):
            title = scrapy.Field()
            url = scrapy.Field()
            posts = scrapy.Field()
            op_account_name = scrapy.Field()

        class Post(scrapy.Item):
            user = scrapy.Field()
            title = scrapy.Field()
            content = scrapy.Field()
            datetime = scrapy.Field()

        def extract_thread_data(response):
            new_thread = Thread()
            new_thread['title'] = response.xpath("//h2[@class='topic-title']/a/text()").extract()[0]
            new_thread['url'] = response.url
            return new_thread

        def extract_post_data(response):
            post_titles = response.xpath("//div[@class='postbody']//h3/a/text()").extract()
            post_users = response.xpath("//div[@class='postbody']//span[@class='username']/text()").extract()
            post_contents = response.xpath("//div[@class='postbody']//div[@class='content']").extract()
            post_datestrings = response.xpath("//div[@class='postbody']//p[@class='author']/text()[3]").extract()
            posts = []
            for title, author, content, datestring in zip(post_titles, post_users, post_contents, post_datestrings):
                new_post = Post()
                new_post['user'] = author
                new_post['title'] = title
                new_post['content'] = ''.join(remove_tags(content)) #We use join here as content is a list, which we want to flatten into a string
                datestring = datestring.replace("\n","").replace("\t","").replace(" ","").replace(":","").replace(",","")
                dt = datetime.datetime.strptime(datestring,"%a%b%d%Y%I%M%p")
                new_post['datetime'] = dt
                posts.append(new_post)
            return posts

        thread = extract_thread_data(response)
        thread['posts'] = extract_post_data(response)
        thread['op_account_name'] = thread['posts'][0]['user']
        return thread

