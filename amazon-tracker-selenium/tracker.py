from config import(get_chrome_options, get_web_driver, set_browser_as_incognito,
                   set_ignore_certificate_error, NAME, CURRENCY, BASE_URL, DIRECTORY)

from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime
import re


class Gen_rep:
    def __init__(self, file_name, base_link, currency, data):
        self.file_name = file_name
        self.data = data
        self.base_link = base_link
        self.currency = currency
        report = {
            'title': self.file_name,
            'date': self.get_now(),
            'cheapest_item': self.cheapest_item(),
            'Most Popular': self.most_popular(),
            'currency': self.currency,
            'base_link': self.base_link,
            'products': self.data

        }
        print("Creating report....")
        with open(f'{DIRECTORY}/{file_name}.json', 'w') as f:
            json.dump(report, f)
        print("Done...")

    def get_now(self):
        now = datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def cheapest_item(self):
        try:
            return sorted(self.data, key=lambda k: k['price'])[0]
        except Exception as e:
            print(e)
            print("Problem with sorting elements")
            return None

    def most_popular(self):
        try:
            return sorted(self.data, key=lambda k: k['number of ratings'])[-1]
        except Exception as e:
            print(e)
            print('problem with sorting number of ratings')
            return None


class amazon_api:
    def __init__(self, search_term, base_url, currency):
        self.base_url = base_url
        self.search_term = search_term
        options = get_chrome_options()
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        self.driver = get_web_driver(options)
        self.currency = currency

    def run(self):
        print('starting script....')
        print(f"Looking for {self.search_term} products...")
        links = self.get_links()
        sleep(1)
        if not links:
            print('stopped script')
            return
        print(f"Got {len(links)} links to products...")
        products = self.get_info(links)
        print(f"Got info about {len(products) } products...")
        self.driver.quit()
        return products

    def get_info(self, links):
        asins = self.get_asins(links)
        products = []
        for asin in asins:
            product = self.get_single_product_info(asin)
            if product:
                products.append(product)
        return products

    def convert_price(self, price):
        price = re.sub("\s", '', price)
        price = re.sub("₹", '', price)
        price = re.sub(",", '', price)
        price = re.sub("$", '', price)
        price = float(price)
        return price

    def get_price(self):
        try:
            price = self.driver.find_element_by_id('priceblock_ourprice').text
            price = self.convert_price(price)
        except NoSuchElementException:
            try:
                price = self.driver.find_element_by_id(
                    'priceblock_dealprice').text
                price = self.convert_price(price)
            except Exception as e:
                print(e)
                print(
                    f"Can't get price of a product  - {self.driver.current_url}")
                return None
        return price

    def get_single_product_info(self, asin):
        print(f"Product ID:{asin} - getting Data...")
        product_short_url = self.shorten_url(asin)
        self.driver.get(f'{product_short_url}')
        sleep(2)
        title = self.get_title()
        seller = self.get_seller()
        price = self.get_price()
        rating = self.get_rating()
        number_of_ratings = self.get_no_of_ratings()
        if title and seller and price:

            product_info = {
                'asin': asin,
                'url': product_short_url,
                'title': title,
                'seller': seller,
                'price': price,
                'rating': rating,
                'number of ratings': number_of_ratings
            }
            return product_info
        else:
            return None

    def get_seller(self):
        try:
            return self.driver.find_element_by_id('bylineInfo').text
        except Exception as e:
            print(e)
            print(f"Can't get seller of a product - {self.driver.current_url}")
            return None

    def get_title(self):
        try:
            return self.driver.find_element_by_id('productTitle').text
        except Exception as e:
            print(e)
            print(f"Can't get title of a product - {self.driver.current_url}")
            return None

    def get_rating(self):
        try:
            rating = self.driver.find_element_by_id('acrPopover')
            rating = rating.get_attribute('title')
            return rating
        except Exception as e:
            return None

    def get_no_of_ratings(self):
        try:
            rating = self.driver.find_element_by_id(
                'acrCustomerReviewText').text
            no_of_ratings = self.get_no_of_ratings_int(rating)
            return no_of_ratings
        except Exception as e:
            return int(0)

    def get_no_of_ratings_int(self, rating):
        if(rating):
            rating = re.sub('\s', '', rating)
            rating = re.sub('ratings', '', rating)
            rating = re.sub(',', '', rating)
            return int(rating)
        else:
            return None

    def shorten_url(self, asin):
        return self.base_url + '/dp/' + asin

    def get_asins(self, links):
        return [self.get_asin(link) for link in links]

    def get_asin(self, product_link):
        return product_link[product_link.find('/dp/') + 4:product_link.find('/ref')]

    def get_links(self):
        self.driver.get(self.base_url)
        element = self.driver.find_element_by_xpath(
            '//*[@id="twotabsearchtextbox"]')
        element.send_keys(self.search_term, Keys.RETURN)
        sleep(2)
        result_list = self.driver.find_elements_by_class_name(
            's-main-slot')

        links = []
        try:

            results = result_list[0].find_elements_by_class_name(
                's-no-outline')
            links = [link.get_attribute('href') for link in results]

            return links
        except Exception as e:
            print("Didn't get any products")
            print(e)
            return links


if __name__ == '__main__':
    amazon = amazon_api(NAME, BASE_URL, CURRENCY)
    data = amazon.run()

    Gen_rep(NAME, BASE_URL, CURRENCY, data)
