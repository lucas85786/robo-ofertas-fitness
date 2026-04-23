import requests
import time
import hashlib
import hmac
import json
import google.generativeai as genai

# DADOS EXATOS DA SUA FOTO
SHOPEE_APP_ID = 18331390798
SHOPEE_SECRET = "2KDGUEBFN66R3W5ZTVA3Y2BM7KBBHCGV" # Se você redefiniu, coloque a NOVA aqui
SUPABASE_URL = "https://oxiswtfwdgkmsnbxrlte.supabase.co/rest/v1/promocoes"
SUPABASE_KEY = "sb_publishable_4DuwwJBZ7JouakUyLRYSMg_69uTblGu"
GEMINI_KEY = "AIzaSyDqg_ypcUYtM01Vrj0Bv1i1TnQkyMssJCI"

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def buscar_produto():
    timestamp = int(time.time())
    path = "/api/v1/offer/search"
    body = {"keyword": "whey", "pageSize": 1}
    body_str = json.dumps(body)
    
    # Cálculo da assinatura padrão Shopee Afiliados
    base = f"{SHOPEE_APP_ID}{path}{timestamp}{body_str}{SHOPEE_SECRET}"
    signature = hmac.new(SHOPEE_SECRET.encode(), base.encode(), hashlib.sha256).hexdigest()

    headers = {
        "Authorization": f"SHA256 {signature}",
        "Timestamp": str(timestamp),
        "AppID": str(SHOPEE_APP_ID),
        "Content-Type": "application/json"
    }

    print("🚀 Testando conexão com a Shopee...")
    res = requests.post(f"https://open-api.affiliate.shopee.com.br{path}", headers=headers, data=body_str)
    
    print(f"Status: {res.status_code}")
    print(f"Resposta: {res.text}")

    if "data" in res.json():
        print("✅ CONECTADO COM SUCESSO!")
        # ... (aqui entraria a parte de salvar no Supabase se funcionar)
    else:
        print("❌ A Shopee ainda recusa a senha.")

if __name__ == "__main__":
    buscar_produto()
