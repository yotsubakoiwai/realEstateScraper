import scrapy


class OtherFeatures(scrapy.Item):
    name = scrapy.Field()
    description = scrapy.Field()


class House(scrapy.Item):
    address = scrapy.Field()
    price = scrapy.Field()
    bed = scrapy.Field()
    bath = scrapy.Field()
    carPark = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    otherFeatures = scrapy.Field()
    url = scrapy.Field()


class RealEstateSpider(scrapy.Spider):
    name = "realestate"

    # start_urls = [
    #     'https://www.realestate.com.au/buy/in-wa/list-1'
    # ]

    def start_requests(self):
        yield scrapy.Request(url='https://www.realestate.com.au/buy/in-wa/list-1', callback=self.parse)

    def parse(self, response):
        for estate in response.css('div.listingInfo.rui-clearfix'):
            house = House()
            house['address'] = estate.css('div.vcard a::text').extract_first()
            house['price'] = estate.css("div.propertyStats > p.priceText").css("::text").extract_first()
            features = estate.css("dl.rui-property-features.rui-clearfix > dd").css("::text").extract()
            if len(features) > 0:
                house['bed'] = features[0]
            if len(features) > 1:
                house['bath'] = features[1]
            if len(features) > 2:
                house['carPark'] = features[2]
            detail_link = estate.css('div.vcard a::attr(href)').extract_first()
            detail_link = response.urljoin(detail_link)
            house['url'] = detail_link
            request = scrapy.Request(detail_link, callback=self.parse_details)
            request.meta['item'] = house
            yield request

            next_page = response.css('li.nextLink a::attr(href)').extract_first()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

    @staticmethod
    def parse_details(response):
        house = response.meta['item']
        primary_content = response.css("div#detailsCont #primaryContent")
        house['title'] = primary_content.css("p.title::text").extract_first()
        house['description'] = primary_content.css("p.body::text").extract()
        other_features = []
        features = response.css("div#detailsCont #primaryContent #features div.featureList").css("ul li")
        for li in features:
            other1 = OtherFeatures()
            other1['name'] = li.css("::text").extract_first()
            other1['description'] = li.css("span::text").extract_first()
            other_features.append(other1)

        house['otherFeatures'] = other_features
        yield house
