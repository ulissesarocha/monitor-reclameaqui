# =============================================
EMPRESA_SLUG = "unifaj-centro-universitario-de-jaguariuna"
EMAIL_DESTINO = "negociosestrategicos.ulisses@unieduk.com.br"
EMAIL_REMETENTE = "negociosestrategicos.ulisses@unieduk.com.br"
# =============================================

import os, json, smtplib
from email.mime.text import MIMEText
from datetime import datetime
from playwright.sync_api import sync_playwright

SENHA_EMAIL = os.environ["GMAIL_SENHA"]
ARQUIVO_VISTO = "reclamacoes_vistas.json"

def buscar_reclamacoes():
    url = f"https://www.reclameaqui.com.br/empresa/{EMPRESA_SLUG}/lista-reclamacoes/?status=NAO_RESPONDIDA"
    reclamacoes = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        items = page.query_selector_all("a[href*='/reclamacao/']")
        for item in items:
            href = item.get_attribute("href")
            titulo = item.inner_text().strip()
            if href and titulo:
                rid = href.strip("/").split("/")[-1]
                reclamacoes.append({"id": rid, "title": titulo, "href": href})
        browser.close()

    # Remove duplicatas por id
    vistos_ids = set()
    unicos = []
    for r in reclamacoes:
        if r["id"] not in vistos_ids:
            vistos_ids.add(r["id"])
            unicos.append(r)
    return unicos

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
        corpo += f"• {r['title']}\n  https://www.reclameaqui.com.br{r['href']}\n\n"
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
    print(f"Total encontrado: {len(reclamacoes)}")
