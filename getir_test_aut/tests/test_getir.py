import pytest
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def take_screenshot(driver, name="screenshot"):
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    driver.save_screenshot(f"{name}_{timestamp}.png")

def extract_number(text):
    """
    Metin içerisindeki ilk ondalıklı sayıyı bulur.
    Exp:  "₺15,75" → 15.75 yapacak, "(531.96/kg)" → 531.96
    """
    match = re.search(r"[\d]+(?:[.,]\d+)?", text)
    if match:
        number_str = match.group(0).replace(",", ".")
        try:
            return float(number_str)
        except ValueError:
            return 0.0
    return 0.0

def scroll_to_bottom(driver, pause_time=1.5):
    """Sayfayı sonuna kadar kaydırır."""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(pause_time)

def load_all_products(driver, pause_time=1.5, max_attempts=10):
    """
    Sayfadaki ürün sayısı değişmeyene kadar kaydırır.
    """
    last_count = 0
    attempts = 0
    while attempts < max_attempts:
        scroll_to_bottom(driver, pause_time)
        all_products = driver.find_elements(By.CSS_SELECTOR, "[data-testid='card']")
        if len(all_products) == last_count:
            break
        last_count = len(all_products)
        attempts += 1
    return all_products

@pytest.fixture(params=["chrome", "firefox"], scope="class")
def driver(request):
    browser = request.param
    if browser == "chrome":
        service = ChromeService()  # chromedriver
        drv = webdriver.Chrome(service=service)
    elif browser == "firefox":
        service = FirefoxService()  # geckodriver
        drv = webdriver.Firefox(service=service)
    else:
        raise ValueError("Unsupported browser")
    drv.maximize_window()
    yield drv
    drv.quit()

def test_getir_shopping_flow(driver):
    driver.get("https://getir.com/")
    WebDriverWait(driver, 10).until(EC.title_contains("Getir"))
    
    # Çerez popup'ını kapatma
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".style__Button-sc-__sc-6ivys6-0.eGRCCQ"))
        )
        cookie_button.click()
    except Exception as e:
        print("Çerez kabul butonu bulunamadı:", e)
    
    try:
        # Fit & Form kategorisini bul ve tıkla
        fit_form_category = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//img[@alt='Fit & Form']"))
        )
        fit_form_category.click()
        
        # "Sepetin şu anda boş" mesajını bekle
        empty_basket_message = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//span[@data-testid='text' and contains(text(),'boş')]"))
        )
        assert "boş" in empty_basket_message.text.lower(), "Sepet boş görünmüyor!"
        
        # Granola alt kategorisini bul ve tıkla
        granola_category = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Granola')]"))
        )
        granola_category.click()
        
        # Tüm ürünlerin yüklenmesi için sayfanın sonuna kadar kaydırırız 
        all_products = load_all_products(driver, pause_time=1.5, max_attempts=10)
        print("Sayfadaki toplam ürün sayısı:", len(all_products))
        
        # Eğer URL'de "granola" varsa, tüm ürünlerin granola olduğunu varsayalım;
        # aksi halde başlığa göre filtreleyelim.
        if "granola" in driver.current_url.lower():
            granola_products = all_products
        else:
            granola_products = []
            for product in all_products:
                try:
                    title = product.find_element(By.CSS_SELECTOR, "[data-testid='title']").text.strip().lower()
                    if "granola" in title:
                        granola_products.append(product)
                except Exception as e:
                    continue
        
        print("Granola alt kategorisinde bulunan ürün sayısı:", len(granola_products))
        if not granola_products:
            raise Exception("Granola alt kategorisine ait ürün bulunamadı!")
        
        # Kategori sayfasındaki fiyatı al 
        def extract_category_price(product):
            try:
                # Ürünün fiyatını içerenleri döngüye al
                price_elements = product.find_elements(By.CSS_SELECTOR, "[data-testid='text']")
                price_text = ""
                for el in price_elements:
                    txt = el.text
                    if "₺" in txt:
                        price_text = txt
                        break
                if not price_text:
                    return 0.0
                print("Kategori ham fiyat metni:", repr(price_text))
                return extract_number(price_text)
            except Exception as e:
                print("Kategori fiyatı çekilemedi:", e)
                return 0.0
        
        # Granola  ürünler arasında en yüksek price veren ürün
        most_expensive_product = max(granola_products, key=extract_category_price)
        max_price = extract_category_price(most_expensive_product)
        print("Granola alt kategorisinde en pahalı ürün fiyatı:", max_price)
        print("En pahalı ürün bulundu. (Adım adım test devam ediyor...)")
        
        # ürün detayı için click görsel
        most_expensive_image = most_expensive_product.find_element(By.CSS_SELECTOR, "[data-testid='main-image']")
        driver.execute_script("arguments[0].scrollIntoView(true);", most_expensive_image)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", most_expensive_image)
        time.sleep(3)
        print("En pahalı ürün görseline tıklandı, detay sayfasına geçildi.")
        
        # Detay sayfasındaki fiyatı çekmek için
        detail_price_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-testid='text']"))
        )
        detail_price_text = ""
        for el in detail_price_elements:
            if "₺" in el.text:
                detail_price_text = el.text
                break
        if not detail_price_text:
            raise Exception("Ürün detay sayfasında fiyat bulunamadı!")
        print("Detay ham fiyat metni:", repr(detail_price_text))
        detail_price = extract_number(detail_price_text)
        print("Ürün detay sayfasındaki fiyat:", detail_price)
        
        # Fiyat karşılaştırması: Toleransı 0.1 olarak ayarladım.
        assert abs(max_price - detail_price) < 0.1, "Kategori fiyatı ile detay sayfası fiyatı eşleşmiyor!"
    
    except Exception as e:
        take_screenshot(driver, "test_failure")
        raise e
