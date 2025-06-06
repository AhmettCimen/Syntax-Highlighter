# C Dili Sözdizimi Vurgulayıcı (C Language Syntax Highlighter)

## 📝 Proje Hakkında

Bu proje, C programlama dili için sözdizimi vurgulama özelliğine sahip bir GUI uygulamasıdır. Uygulama, sözdizimi analizi, sözcüksel analiz ve ayrıştırma işlemlerini formal bir gramer yapısına dayalı olarak gerçekleştirir.

### 🎯 Temel Özellikler

- Sözdizimi vurgulama
- Gelişmiş GUI arayüzü
- Detaylı hata tespiti ve raporlama
- Token analizi ve görselleştirme
- Ayrıştırma ağacı (Parse Tree) görselleştirme

## 🔍 Teknik Detaylar ve Yaklaşımlar

### Sözcüksel Analiz (Lexical Analysis)

Projede "State Diagram & Program Implementation" yaklaşımı tercih edilmiştir. Bu yaklaşım:

- Regular expressions kullanarak token tanımlamalarını gerçekleştirir
- Esnek ve genişletilebilir bir yapı sunar
- Performans optimizasyonuna olanak sağlar

Token tipleri:

- Anahtar Kelimeler (int, char, float, vb.)
- Tanımlayıcılar (değişken ve fonksiyon isimleri)
- Sayılar
- Stringler
- Operatörler
- Ayırıcılar
- Preprocessorlar
- Headerlar

### Ayrıştırıcı (Parser)

"Top-Down Parsing" yaklaşımı kullanılmıştır:

- Recursive Descent Parser implementasyonu
- Preorder traversal ile parse tree oluşturma
- Detaylı hata tespiti ve raporlama
- Sözdizimi kurallarının hiyerarşik analizi

### Performans Optimizasyonu

- Analiz programa herhangi bir veri girişi/çıkışı yapıldığında başlar
- Her an kontrol ve analiz yerine veri değişikliklerinde çalıştığı için verimlilik sağlar
- Kullanıcı kontrolünde analiz imkanı sunar

### 🎨 Token Renk Şeması

| Token Tipi             | Renk              | Örnek                   |
| ---------------------- | ----------------- | ----------------------- |
| Anahtar Kelimeler      | Mavi              | `int`, `void`, `return` |
| Stringler              | Yeşil             | `"Hello World"`         |
| Yorumlar               | Açık Yeşil        | `// Bu bir yorum`       |
| Preprocessorlar        | Mor               | `#include`              |
| Sayılar                | Kırmızı           | `42`, `3.14`            |
| Operatörler            | Siyah             | `+`, `-`, `*`, `/`      |
| Parametreler           | Turuncu           | `void foo(int param)`   |
| Hata Vurgulaması       | Kırmızı Arka Plan | Sözdizimi hataları      |

## 💻 Kurulum

1. Python 3.x'in yüklü olduğundan emin olun
2. Projeyi klonlayın:

```bash
git clone [https://github.com/AhmettCimen/Syntax-Highlighter]
```

3. Gerekli bağımlılıkları yükleyin:

```bash
pip install tkinter
```

## 🚀 Kullanım

1. Uygulamayı başlatın:

```bash
python gui.py
```

2. Metin editörüne C kodunuzu yazın veya yapıştırın
3. Hataları görmek için "Errors" sekmesini kontrol edin
4. Token listesi ve ayrıştırma ağacını incelemek için ilgili sekmeleri kullanın

## 📹 Video

[Video linki eklenecek]
