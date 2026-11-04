import requests
import urllib.parse
import os

# ==========================================
# 1. الإعدادات والمعلومات الشخصية
# ==========================================
WP_URL = "https://takeainformation.com"  # رابط موقعك
PINTEREST_ACCESS_TOKEN = "pina_AMA5P3YYAAF2MAAAGAAD7XGQ2KNIIBQBIQD3YWTB3BVB76GRFNGV26HX6RFDJZJZUAYE2DOAJGQSJS375SELWWX7O32OIA"  # Access Token ديالك
PINTEREST_BOARD_ID = "1102819096194222618"  # Board ID ديال Delicious food

# ==========================================
# 2. جلب أحدث المقالات من WordPress
# ==========================================
def get_latest_posts(limit=1):
    wp_api_url = f"{WP_URL}/wp-json/wp/v2/posts?_embed&per_page={limit}"
    response = requests.get(wp_api_url)
    
    if response.status_code != 200:
        print("❌ خطأ في الاتصال بموقع WordPress")
        return []
        
    posts = response.json()
    extracted_posts = []
    
    for post in posts:
        title = post['title']['rendered']
        link = post['link']
        
        # محاولة جلب الصورة البارزة للمقال (Featured Image)
        image_url = None
        if '_embedded' in post and 'wp:featuredmedia' in post['_embedded']:
            media = post['_embedded']['wp:featuredmedia'][0]
            image_url = media.get('source_url')
        
        # إذا ماكانتش تصويرة للمقال، كنولدو تصويرة مجانية عبر Pollinations.ai
        if not image_url:
            encoded_title = urllib.parse.quote(title)
            image_url = f"https://image.pollinations.ai/prompt/delicious%20food%20recipe%20{encoded_title}?width=1000&height=1500&nologo=true"
            
        extracted_posts.append({
            'title': title,
            'link': link,
            'image_url': image_url
        })
        
    return extracted_posts

# ==========================================
# 3. النشر في Pinterest عبر API v5
# ==========================================
def create_pinterest_pin(title, post_url, image_url):
    pin_url = "https://api.pinterest.com/v5/pins"
    
    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "board_id": PINTEREST_BOARD_ID,
        "title": title[:100],  # Pinterest كيقبل أقصى حد 100 حرف فالعنوان
        "description": f"Check out this amazing post: {title}. Read more on our website!",
        "link": post_url,
        "media_source": {
            "source_type": "image_url",
            "url": image_url
        }
    }
    
    response = requests.post(pin_url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        print(f"✅ تم النشر بنجاح: {title}")
        print(f"🔗 رابط المنشور: {response.json().get('id')}")
    else:
        print(f"❌ خطأ فـ Pinterest API: {response.status_code}")
        print(response.text)

# ==========================================
# 4. تشغيل العملية
# ==========================================
if __name__ == "__main__":
    print("[*] جاري البحث عن مقالات جديدة...")
    latest_posts = get_latest_posts(limit=1)
    
    for p in latest_posts:
        print(f"[*] جاري نشر المقال: {p['title']}")
        create_pinterest_pin(p['title'], p['link'], p['image_url'])
