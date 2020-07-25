from selenium import webdriver


DIRECTORY = 'reports'
NAME = ''
# add item name here
CURRENCY = '₹'

BASE_URL = 'https://www.amazon.in/'


def get_web_driver(options):
    return webdriver.Chrome(r'', chrome_options=options)

# add chromedriver path here


def get_chrome_options():
    return webdriver.ChromeOptions()


def set_ignore_certificate_error(options):
    options.add_argument('--ignore-certificate-errors')


def set_browser_as_incognito(options):
    options.add_argument('--incognito')
