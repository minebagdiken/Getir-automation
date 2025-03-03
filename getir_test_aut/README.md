Getir

Bu proje, Selenium ve pytest kullanılarak hazırlanmış bir web otomasyon testidir.
Aşağıdaki adımları izleyerek projeyi çalıştırabilirsiniz.

Adım 1: Projeyi Klonlayın
--------------------------------
Terminal veya CMD üzerinde aşağıdaki komutları çalıştırın:

  git clone https://github.com/kullanici_adiniz/proje_adi.git
  cd proje_adi

Adım 2: Sanal Ortam Oluşturun
--------------------------------
Projeyi izole bir ortamda çalıştırmak için bir sanal ortam oluşturun.

Windows:
  python -m venv venv
  venv\Scripts\activate


Adım 3: Gerekli Paketleri Yükleyin
--------------------------------
Projede kullanılan tüm bağımlılıklar "requirements.txt" dosyasında belirtilmiştir.
Aşağıdaki komutla paketleri yükleyin:

  pip install -r requirements.txt

Not:
  - Eğer "webdriver-manager" kullanılıyorsa, Chrome ve Firefox için gerekli sürücüler otomatik olarak indirilecektir.
  - Eğer sürücüleri manuel eklemeyi tercih ederseniz, sisteminizdeki Chrome sürümüne uygun chromedriver.exe dosyasını projenin kök dizinine ekleyin.

Adım 4: Testleri Çalıştırın
--------------------------------
Testleri çalıştırmak için:

  pytest

Testler çalıştırıldıktan sonra, çıktıyı terminalden görebilirsiniz.
Hata durumunda ekran görüntüleri (screenshot) proje dizininde kaydedilecektir.
