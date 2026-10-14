import time
import requests
from web3 import Web3

# ==================== إعدادات البوت الخبير ====================
COLLECTION_SLUG = "pudgypenguins"      # اسم المجموعة
OFFICIAL_CONTRACT = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8" # العنوان الاصلي للعقد (للتحقق)
MAX_BUY_PRICE = 0.5                  # أقصى سعر شراء (ETH)
MIN_COLLECTION_VOLUME = 50.0          # أدنى حجم تداول مسموح لضمان أصلية المجموعة (ETH)

OPENSEA_API_KEY = "YOUR_OPENSEA_API_KEY"

# شبكة Base أو الإيثريوم
RPC_URL = "https://mainnet.base.org"
PRIVATE_KEY = "YOUR_BURNER_WALLET_PRIVATE_KEY" 
WALLET_ADDRESS = "YOUR_WALLET_ADDRESS"

w3 = Web3(Web3.HTTPProvider(RPC_URL))
# =============================================================

def verify_collection_authenticity():
    """فحص خبير: التحقق من أصلية المجموعة، التوثيق، وحجم السيولة"""
    url = f"https://api.opensea.io/api/v2/collections/{COLLECTION_SLUG}"
    headers = {"accept": "application/json", "x-api-key": OPENSEA_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            # 1. التحقق من التوثيق الرسمى
            is_verified = data.get('safelist_request_status') == 'verified'
            
            # 2. التحقق من حجم التداول الإجمالي
            stats = data.get('stats', {})
            total_vol = stats.get('total_volume', 0)
            
            if not is_verified:
                print("⚠️ [تحذير أمني] المجموعة غير موثوقة بعلامة التوثيق الأزرق! تم إلغاء الشراء.")
                return False
                
            if total_vol < MIN_COLLECTION_VOLUME:
                print(f"⚠️ [تحذير سيولة] حجم تداول المجموعة ({total_vol} ETH) أقل من الحد الآمن.")
                return False
                
            print("✅ [فحص الأمان] المجموعة أصلية، موثقة، ولديها سيولة عالية.")
            return True
            
        return False
    except Exception as e:
        print(f"[!] خطأ أثناء فحص أمان المجموعة: {e}")
        return False

def get_best_listing():
    """جلب أفضل عرض مع التحقق من السعر"""
    url = f"https://api.opensea.io/api/v2/listings/collection/{COLLECTION_SLUG}/best"
    headers = {"accept": "application/json", "x-api-key": OPENSEA_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            price_data = data.get('price', {}).get('current', {})
            val = price_data.get('value')
            decimals = price_data.get('decimals', 18)
            if val:
                actual_price = int(val) / (10 ** decimals)
                return actual_price, data
        return None, None
    except Exception as e:
        print(f"[!] خطأ في جلب العروض: {e}")
        return None, None

def execute_smart_trade(order_data, price):
    """تنفيذ الشراء الآلي بعد اجتياز جميع شروط الأمان"""
    print(f"🚀 [صفقة معتمدة] السعر ({price} ETH) ممتاز والمجموعة أصلية! جاري الشراء...")
    try:
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
        tx = {
            'nonce': nonce,
            'to': OFFICIAL_CONTRACT,
            'value': w3.to_wei(price, 'ether'),
            'gas': 250000,
            'gasPrice': w3.to_wei('0.1', 'gwei'),
            'data': '0x...' 
        }
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"🎉 تم الشراء بنجاح! رقم المعاملة: {w3.to_hex(tx_hash)}")
    except Exception as e:
        print(f"[!] فشل إرسال المعاملة: {e}")

def main():
    print(f"=== بدء تشغيل البوت الخبير لمراقبة: {COLLECTION_SLUG} ===")
    
    # إجراء فحص الأمان مرة عند البداية
    if not verify_collection_authenticity():
        print("❌ توقف البوت لحماية محفظتك من المجموعات المزيفة أو الضيفة.")
        return

    while True:
        price, order_data = get_best_listing()
        if price is not None:
            print(f"[{time.strftime('%H:%M:%S')}] السعر الحقيقي الآن: {price} ETH")
            if price <= MAX_BUY_PRICE:
                execute_smart_trade(order_data, price)
                break
        else:
            print("جاري التحليل والمراقبة...")
            
        time.sleep(15)

if __name__ == "__main__":
    main()
      
