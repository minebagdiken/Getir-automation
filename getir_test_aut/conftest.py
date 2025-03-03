from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import pytest

@pytest.fixture(params=["chrome", "firefox"], scope="class")
def driver(request):
    browser = request.param
    if browser == "chrome":
        drv = webdriver.Chrome(service=ChromeService(ChromeDriverManager(version="133.0.6943.142").install()))
    elif browser == "firefox":
        drv = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    else:
        raise ValueError("Unsupported browser")
    drv.maximize_window()
    yield drv
    drv.quit()
