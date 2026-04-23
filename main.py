import os
import requests
import time
import hashlib
import json
import google.generativeai as genai

# --- CONFIGURAÇÕES DO LUCAS ---
SHOPEE_APP_ID = 18331390798
SHOPEE_SECRET = "2KDGUEBFN66R3W5ZTVA3Y2BM7KBBHCGV"
SUPABASE_URL = "https://oxiswtfwdgkmsnbxrlte.supabase.co/rest/v1/promocoes"
SUPABASE_KEY = "sb_publishable_4DuwwJBZ7JouakUyLRYSMg_69uTblGu"
GEMINI_KEY = "AIzaSyDqg_ypcUYtM01Vrj0Bv1i1TnQkyMssJCI"

# Configuração da IA
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def buscar_e_postar():
    try:
        # 1. Preparar a Chamada (Usando a URL de consulta de produtos)
        timestamp = int(time.time())
        path = "/api/v1/offer/search"
        
        # O segredo está aqui: o corpo precisa ser exatamente o que a Shopee espera
        body = {"keyword": "whey protein", "pageSize": 10}
        body_str = json.dumps(body)
        
        # Gerar a assinatura SHA256 (O jeito que a Shopee gosta)
        base_string = f"{SHOPEE_APP_ID}{timestamp}{body_str}{SHOPEE_SECRET}"
        signature = hashlib.sha256(base_string.encode()).hexdigest()
        
        url = f"https://open-api.affiliate.shopee.com.br{path}"
        
        headers = {
            "AppID": str(SHOPEE_APP_ID),
            "Timestamp": str(timestamp),
            "Authorization": f"SHA256 {signature}",
            "Content-Type": "application/json"
        }

        print("🔎 Buscando oferta de Afiliado na Shopee...")
        res = requests.post(url, headers=headers, data=body_str)
        dados = res.json()

        if 'data' in dados and 'list' in dados['data'] and len(dados['data']['list']) > 0:
            produto = dados['data']['list'][0]
            nome = produto.get('productName', 'Produto')
            # Esse link abaixo já é o seu link de rastreio de Afiliado
            link_afiliado = produto.get('offerLink', '')
            
            print(f"✅ Produto encontrado! Gerando post para: {nome}")

            # 2. Criar o texto com a IA
            prompt = f"Crie um post animado para WhatsApp sobre: {nome}. Use emojis de academia."
            response = model.generate_content(prompt)
            texto_venda = response.text

            # 3. Salvar no Supabase
            headers_supa = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            
            dados_supa = {
                "titulo": nome,
                "preco": "OFERTA",
                "cupom": "FITNESS",
                "link": link_afiliado, 
                "texto_ia": texto_venda
            }
            
            requests.post(SUPABASE_URL, json=dados_supa, headers=headers_supa)
            print(f"🚀 SUCESSO! Oferta postada com seu link de afiliado!")
        else:
            print(f"❌ Erro da Shopee: {dados}")

    except Exception as e:
        print(f"⚠️ Erro no robô: {str(e)}")

if __name__ == "__main__":
    buscar_e_postar()
