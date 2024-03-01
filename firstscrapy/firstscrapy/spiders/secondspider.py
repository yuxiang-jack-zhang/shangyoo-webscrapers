import scrapy
from ..items import keyboardProduct
from ..itemsloaders import keyboardProductLoader


class SecondspiderSpider(scrapy.Spider):
    name = "secondspider"
    allowed_domains = ["nuphy.com"]
    start_urls = ["https://nuphy.com/collections/keyboards"]

    def parse(self, response):
        products = response.css("div.grid-item.grid-product")
        
        product_item = keyboardProduct()
        for product in products:
            keyboard = keyboardProductLoader(item = keyboardProduct(), selector = product)
            keyboard.add_css('name', "div.grid-product__title::text")
            keyboard.add_css('price', "span.money::text")
            keyboard.add_css('url', "div.grid-item__content a::attr(href)")
            yield keyboard.load_item()
