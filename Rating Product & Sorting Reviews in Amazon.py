
###################################################
# PROJE: Rating Product & Sorting Reviews in Amazon
###################################################

###################################################
# İş Problemi
###################################################

# E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
# Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak, satıcılar için ürünün öne çıkması ve satın
# alanlar için sorunsuz bir alışveriş deneyimi demektir. Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması
# olarak karşımıza çıkmaktadır. Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp
# hem de müşteri kaybına neden olacaktır. Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler
# ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

###################################################
# Veri Seti Hikayesi
###################################################

# Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
# Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

# Değişkenler:
# reviewerID: Kullanıcı ID’si
# asin: Ürün ID’si
# reviewerName: Kullanıcı Adı
# helpful: Faydalı değerlendirme derecesi
# reviewText: Değerlendirme
# overall: Ürün rating’i
# summary: Değerlendirme özeti
# unixReviewTime: Değerlendirme zamanı
# reviewTime: Değerlendirme zamanı Raw
# day_diff: Değerlendirmeden itibaren geçen gün sayısı
# helpful_yes: Değerlendirmenin faydalı bulunma sayısı
# total_vote: Değerlendirmeye verilen oy sayısı



###################################################
# GÖREV 1: Average Rating'i Güncel Yorumlara Göre Hesaplayınız ve Var Olan Average Rating ile Kıyaslayınız.
###################################################

# Paylaşılan veri setinde kullanıcılar bir ürüne puanlar vermiş ve yorumlar yapmıştır.
# Bu görevde amacımız verilen puanları tarihe göre ağırlıklandırarak değerlendirmek.
# İlk ortalama puan ile elde edilecek tarihe göre ağırlıklı puanın karşılaştırılması gerekmektedir.

import pandas as pd
from scipy.stats import norm
import numpy as np


###################################################
# Adım 1: Veri Setini Okutunuz ve Ürünün Ortalama Puanını Hesaplayınız.
###################################################

# Load the dataset
df = pd.read_csv('amazon_reviews.csv')  # Assuming the dataset is in a CSV file

# Calculate the average rating
average_rating = df['overall'].mean()
print(f"Average Rating: {average_rating}")

###################################################
# Adım 2: Tarihe Göre Ağırlıklı Puan Ortalamasını Hesaplayınız.
###################################################

# Define a function to calculate the time-weighted average rating
def time_weighted_average(df, time_col='day_diff', rating_col='overall'):
  # Normalize the time column to use as weights
  df['time_weight'] = 1 / (df[time_col] + 1)
  weighted_sum = (df[rating_col] * df['time_weight']).sum()
  total_weight = df['time_weight'].sum()
  return weighted_sum / total_weight

# Calculate the time-weighted average rating
time_weighted_avg_rating = time_weighted_average(df)
print(f"Time-Weighted Average Rating: {time_weighted_avg_rating}")

###################################################
# Görev 2: Ürün için Ürün Detay Sayfasında Görüntülenecek 20 Review'i Belirleyiniz.
###################################################

print(f"Initial Average Rating: {average_rating}")
print(f"Time-Weighted Average Rating: {time_weighted_avg_rating}")

# Comment on the comparison
if time_weighted_avg_rating > average_rating:
  print("The time-weighted average rating is higher, indicating recent reviews are more positive.")
else:
  print("The time-weighted average rating is lower, indicating recent reviews are less positive.")


###################################################
# Adım 1. helpful_no Değişkenini Üretiniz
###################################################

# Not:
# total_vote bir yoruma verilen toplam up-down sayısıdır.
# up, helpful demektir.
# veri setinde helpful_no değişkeni yoktur, var olan değişkenler üzerinden üretilmesi gerekmektedir.

# Create the helpful_no variable
df['helpful_no'] = df['total_vote'] - df['helpful_yes']

###################################################
# Adım 2. score_pos_neg_diff, score_average_rating ve wilson_lower_bound Skorlarını Hesaplayıp Veriye Ekleyiniz
###################################################

# Function to calculate score_pos_neg_diff
def score_pos_neg_diff(yes, no):
  return yes - no

# Function to calculate score_average_rating
def score_average_rating(yes, total):
  return yes / total if total != 0 else 0

# Function to calculate wilson_lower_bound
def wilson_lower_bound(yes, total, confidence=0.95):
  if total == 0:
      return 0
  z = norm.ppf(1 - (1 - confidence) / 2)
  phat = yes / total
  return (phat + z**2 / (2 * total) - z * np.sqrt((phat * (1 - phat) + z**2 / (4 * total)) / total)) / (1 + z**2 / total)

# Calculate and add scores to the DataFrame
df['score_pos_neg_diff'] = df.apply(lambda x: score_pos_neg_diff(x['helpful_yes'], x['helpful_no']), axis=1)
df['score_average_rating'] = df.apply(lambda x: score_average_rating(x['helpful_yes'], x['total_vote']), axis=1)
df['wilson_lower_bound'] = df.apply(lambda x: wilson_lower_bound(x['helpful_yes'], x['total_vote']), axis=1)

##################################################
# Adım 3. 20 Yorumu Belirleyiniz ve Sonuçları Yorumlayınız.
###################################################

# Sort by wilson_lower_bound and select the top 20 reviews
top_20_reviews = df.sort_values('wilson_lower_bound', ascending=False).head(20)

# Display the top 20 reviews
print(top_20_reviews[['reviewerID', 'reviewText', 'wilson_lower_bound']])

# Comment on the results
print("The top 20 reviews have been selected based on the Wilson Lower Bound score, which balances the helpfulness and reliability of the reviews.")

