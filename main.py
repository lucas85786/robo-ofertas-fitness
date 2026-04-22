import os
import requests
import time
import hashlib
import hmac
import json
import google.generativeai as genai

# --- CONFIGURAÇÕES QUE RECUPEREI PARA VOCÊ ---
SHOPEE_APP_ID = 18331390798
SHOPEE_SECRET = "GOTTQIK5CACIRDEAPSKQ57CKQWDYFCAD"
SUPABASE_URL = "https://oxiswtfwdgkmsnbxrlte.supabase.co/rest/v1/promocoes"
SUPABASE_KEY = "sb_publishable_4DuwwJBZ7JouakUyLRYSMg_69uTblGu"
GEMINI_KEY = "AIzaSyDqg_ypcUYtM01Vrj0Bv1i1TnQkyMssJCI"

# Configuração da IA
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def gerar_assinatura(path, body_string):
    """Gera a assinatura de segurança para a API da Shopee"""
    timestamp = int(time.time())
    base_string = f"{SHOPEE_APP_ID}{path}{timestamp}{body_string}{SHOPEE_SECRET}"
    sign = hmac.new(SHOPEE_SECRET.encode(), base_string.encode(), hashlib.sha256).hexdigest()
    return timestamp, sign

def buscar_e_postar():
    try:
        path = "/api/v1/offer/search"
        url = f"https://open-api.affiliate.shopee.com.br{path}"
        
        # O nicho que você escolheu: Fitness/Academia
        body = {"keyword": "whey protein creatina academia", "pageSize": 1}
        body_string = json.dumps(body)
        
        timestamp, sign = gerar_assinatura(path, body_string)
        
        headers_shopee = {
            "Authorization": f"SHA256 {sign}",
            "Timestamp": str(timestamp),
            "AppID": str(SHOPEE_APP_ID),
            "Content-Type": "application/json"
        }

        print("🔎 Buscando a melhor oferta fitness na Shopee...")
        res_shopee = requests.post(url, headers=headers_shopee, data=body_string)
        dados_shopee = res_shopee.json()

        # Verifica se encontrou algum produto
        if 'data' in dados_shopee and len(dados_shopee['data']['list']) > 0:
            produto = dados_shopee['data']['list'][0]
            nome = produto['productName']
            link = produto['offerLink']
            
            print(f"✅ Produto encontrado: {nome}")
            print("🤖 Gemini criando o post maromba...")

            # Prompt personalizado para o seu nicho
            prompt = f"Crie um post estilo 'maromba' para WhatsApp sobre: {nome}. Use muitos emojis de academia, foque no shape e no preço promocional. Seja bem animado!"
            response = model.generate_content(prompt)
            texto_venda = response.text

            # Monta os dados para o seu Supabase
            dados_supa = {
                "titulo": nome,
                "preco": "OFERTA",
                "cupom": "FITNESS",
                "link": link, 
                "texto_ia": texto_venda
            }
            
            headers_supa = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            
            # Envia para o Banco de Dados
            requests.post(SUPABASE_URL, json=dados_supa, headers=headers_supa)
            print(f"🚀 TUDO PRONTO! A oferta de {nome} já está no seu site!")
        else:
            print("❌ Nenhum produto encontrado no momento.")

    except Exception as e:
        print(f"⚠️ Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    buscar_e_postar()
