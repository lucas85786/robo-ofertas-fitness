import os
import requests
import time
import hashlib
import hmac
import json
import google.generativeai as genai

# --- CONFIGURAÇÕES DO LUCAS ---
SHOPEE_APP_ID = 18331390798
SHOPEE_SECRET = "GOTTQIK5CACIRDEAPSKQ57CKQWDYFCAD"
SUPABASE_URL = "https://oxiswtfwdgkmsnbxrlte.supabase.co/rest/v1/promocoes"
SUPABASE_KEY = "sb_publishable_4DuwwJBZ7JouakUyLRYSMg_69uTblGu"
GEMINI_KEY = "AIzaSyDqg_ypcUYtM01Vrj0Bv1i1TnQkyMssJCI"

# Configuração da IA
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def gerar_assinatura(path, body_string):
    timestamp = int(time.time())
    base_string = f"{SHOPEE_APP_ID}{path}{timestamp}{body_string}{SHOPEE_SECRET}"
    sign = hmac.new(SHOPEE_SECRET.encode(), base_string.encode(), hashlib.sha256).hexdigest()
    return timestamp, sign

def buscar_e_postar():
    try:
        path = "/api/v1/offer/search"
        url = f"https://open-api.affiliate.shopee.com.br{path}"
        
        # BUSCA AMPLA PARA TESTE: Celular, Fone e Whey
        body = {"keyword": "celular fone whey bluetooth", "pageSize": 10}
        body_string = json.dumps(body)
        
        timestamp, sign = gerar_assinatura(path, body_string)
        
        headers_shopee = {
            "Authorization": f"SHA256 {sign}",
            "Timestamp": str(timestamp),
            "AppID": str(SHOPEE_APP_ID),
            "Content-Type": "application/json"
        }

        print("🔎 Buscando produtos variados na Shopee para teste...")
        res_shopee = requests.post(url, headers=headers_shopee, data=body_string)
        dados_shopee = res_shopee.json()

        # Verifica se a Shopee devolveu a lista de produtos
        if 'data' in dados_shopee and 'list' in dados_shopee['data'] and len(dados_shopee['data']['list']) > 0:
            produto = dados_shopee['data']['list'][0]
            nome = produto.get('productName', 'Produto Sem Nome')
            link = produto.get('offerLink', '')
            
            print(f"✅ Sucesso! Produto encontrado: {nome}")
            print("🤖 Gemini criando o post de venda...")

            prompt = f"Crie um post de oferta curto para WhatsApp sobre: {nome}. Use emojis e chame a atenção para o preço."
            response = model.generate_content(prompt)
            texto_venda = response.text

            # Enviar para o Supabase
            headers_supa = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal" # Instrução para o Supabase processar rápido
            }

            dados_supa = {
                "titulo": nome,
                "preco": "OFERTA",
                "cupom": "PROMO",
                "link": link, 
                "texto_ia": texto_venda
            }
            
            print("📤 Enviando para o Banco de Dados...")
            envio = requests.post(SUPABASE_URL, json=dados_supa, headers=headers_supa)
            
            if envio.status_code in [200, 201]:
                print("🚀 TUDO OK! A oferta já está no Supabase!")
            else:
                print(f"❌ Erro ao salvar no Supabase: {envio.status_code} - {envio.text}")
        else:
            print("❌ Shopee não encontrou produtos com essas palavras.")
            print(f"Resposta da Shopee: {dados_shopee}")

    except Exception as e:
        print(f"⚠️ Erro Geral: {str(e)}")

if __name__ == "__main__":
    buscar_e_postar()
