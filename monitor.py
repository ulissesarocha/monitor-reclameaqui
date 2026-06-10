# =============================================
# CONFIGURE APENAS ESTAS 3 VARIÁVEIS:
EMPRESA_SLUG = "unifaj-centro-universitario-de-jaguariuna"  # Ex: "magazine-luiza" (pega da URL do Reclame Aqui)
EMAIL_DESTINO = "negociosestrategicos.ulisses@unieduk.com.br"
EMAIL_REMETENTE = "negociosestrategicos.ulisses@unieduk.com.br"
# A senha do Gmail vai em Settings > Secrets (explicado abaixo)
# =============================================

import requests, smtplib, os, json
from email.mime.text import MIMEText
from datetime import datetime

SENHA_EMAIL = os.environ["GMAIL_SENHA"]
ARQUIVO_VISTO = "reclamacoes_vistas.json"

def buscar_reclamacoes():
    url = "https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/query/companyComplains/10/1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Origin": "https://www.reclameaqui.com.br",
        "Referer": f"https://www.reclameaqui.com.br/empresa/{EMPRESA_SLUG}/",
    }
    params = {
        "company": EMPRESA_SLUG,
        "status": "NOT_ANSWERED",
        "order": "CREATED_DATE",
    }
    r = requests.get(url, params=params, headers=headers, timeout=15)
    print(f"Status HTTP: {r.status_code}")
    print(f"Resposta: {r.text[:500]}")
    data = r.json()
    return data.get("complains", {}).get("data", [])

def carregar_vistos():
    if os.path.exists(ARQUIVO_VISTO):
        with open(ARQUIVO_VISTO) as f:
            return set(json.load(f))
    return set()

def salvar_vistos(ids):
    with open(ARQUIVO_VISTO, "w") as f:
        json.dump(list(ids), f)

def enviar_email(novas):
    corpo = f"Você tem {len(novas)} nova(s) reclamação(ões) sem resposta no Reclame Aqui:\n\n"
    for r in novas:
        titulo = r.get("title", "Sem título")
        rid = r.get("id", "")
        corpo += f"• {titulo}\n  https://www.reclameaqui.com.br/reclamacao/{rid}/\n\n"
    
    msg = MIMEText(corpo)
    msg["Subject"] = f"⚠️ {len(novas)} reclamação(ões) nova(s) no Reclame Aqui"
    msg["From"] = EMAIL_REMETENTE
    msg["To"] = EMAIL_DESTINO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_REMETENTE, SENHA_EMAIL)
        smtp.send_message(msg)
    print("E-mail enviado!")

def main():
    print(f"Verificando em {datetime.now()}...")
    reclamacoes = buscar_reclamacoes()
    vistos = carregar_vistos()
    ids_atuais = {str(r["id"]) for r in reclamacoes}
    novas = [r for r in reclamacoes if str(r["id"]) not in vistos]

    if novas:
        print(f"{len(novas)} nova(s) encontrada(s). Enviando e-mail...")
        enviar_email(novas)
        salvar_vistos(vistos | ids_atuais)
    else:
        print("Nenhuma reclamação nova.")

main()
