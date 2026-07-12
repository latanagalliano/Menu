#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 Crea le tabelle "Categorie" e "Testi sito" — La Tana
============================================================
Da lanciare DOPO crea_base_airtable.py.

Su Colab:
     import urllib.request
     code = urllib.request.urlopen("https://raw.githubusercontent.com/latanagalliano/Menu/main/crea_liste_airtable.py").read().decode()
     exec(code)

Non crea doppioni: se una tabella esiste gia' con righe dentro, salta.
============================================================
"""

import json, sys, time, getpass
import urllib.request, urllib.error

API = "https://api.airtable.com/v0"
BASE_NAME = "Menu La Tana"

# (Nome, Sottotitolo, Ordine) — i Nomi devono combaciare con la tendina
# "Categoria" della tabella Piatti.
CATEGORIE = [
    ("Antipasti", "per cominciare", 1),
    ("Primi", "dalla cucina", 2),
    ("Contorni", "da accompagnare", 3),
    ("Pizze", "dal nostro forno", 4),
    ("Aggiunte", "Tutte le pizze anche con farina integrale", 5),
    ("Birre", "alla spina e in bottiglia", 6),
    ("Vini", "della casa e in bottiglia", 7),
    ("Bevande", "analcolici e caffetteria", 8),
]

# (Chiave, Etichetta, Testo, Ordine)
# La "Chiave" e' tecnica: NON va cambiata. Si modifica solo "Testo".
# Un Testo lasciato vuoto = quella riga sparisce dal sito.
TESTI = [
    ("nome_locale", "Nome del locale (titolo grande)", "La Tana", 1),
    ("sopratitolo", "Sopratitolo (riga piccola sopra al nome)", "", 2),
    ("sottotitolo", "Sottotitolo (riga piccola sotto al nome)", "Pizzeria", 3),
    ("motto", "Motto / frase sotto il titolo (vuoto = non compare)", "«Da noi si sta bene, come in una tana.»", 4),
    ("coperto", "Coperto — solo il numero, es. 2 (vuoto = non compare)", "", 5),
    ("nota_surgelati", "Nota surgelati (in fondo alla pagina)", "* prodotto surgelato all'origine o congelato in loco", 6),
    ("nota_vegetariano", "Nota vegetariano (in fondo alla pagina)", "piatto vegetariano", 7),
    ("nota_vegetariano", "Nota vegetariano (in fondo alla pagina)", "piatto vegetariano", 7),
    ("nota_allergeni", "Nota allergeni (in fondo alla pagina)", "Menù allergeni e informazioni sugli ingredienti disponibili su richiesta.", 8),
    ("nota_legenda_allergeni", "Nota nel popup della legenda allergeni", "Menù allergeni completo e informazioni sugli ingredienti disponibili su richiesta. Rif. Reg. UE 1169/2011.", 9),
]


def req(method, url, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Authorization", "Bearer " + token)
    r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try: body = json.loads(body)
        except: pass
        return e.code, body


def find_base(token):
    st, res = req("GET", API + "/meta/bases", token)
    if st != 200:
        print("ERRORE (%s): %s" % (st, res)); return None
    bases = res.get("bases", [])
    for b in bases:
        if b.get("name","").strip() == BASE_NAME:
            return b["id"]
    if len(bases) == 1:
        print("Uso l'unica base visibile: %s" % bases[0].get("name"))
        return bases[0]["id"]
    print("Base '%s' non trovata. Visibili:" % BASE_NAME)
    for b in bases: print("  -", b.get("name"), b["id"])
    return None


def get_table(token, base_id, name):
    st, res = req("GET", API + "/meta/bases/%s/tables" % base_id, token)
    if st != 200: return None
    for t in res.get("tables", []):
        if t.get("name") == name: return t
    return None


def create_table(token, base_id, name, fields):
    st, res = req("POST", API + "/meta/bases/%s/tables" % base_id, token,
                  {"name": name, "fields": fields})
    if st == 200:
        print("  Tabella '%s' creata." % name); return res["id"]
    if st == 422 and "DUPLICATE" in json.dumps(res).upper():
        t = get_table(token, base_id, name)
        if t:
            print("  Tabella '%s' esisteva gia': la riuso." % name); return t["id"]
    print("  ERRORE creando '%s' (%s): %s" % (name, st, res)); return None


def table_has_rows(token, base_id, table_id):
    st, res = req("GET", API + "/%s/%s?maxRecords=1" % (base_id, table_id), token)
    return st == 200 and len(res.get("records", [])) > 0


def insert(token, base_id, table_id, records):
    ok = 0
    for i in range(0, len(records), 10):
        st, res = req("POST", API + "/%s/%s" % (base_id, table_id), token,
                      {"records": records[i:i+10], "typecast": True})
        if st == 200:
            ok += len(res.get("records", []))
        else:
            print("  ERRORE inserimento (%s): %s" % (st, res)); return ok
        time.sleep(0.25)
    return ok


def main():
    print("="*52)
    print(" Tabelle 'Categorie' e 'Testi sito' — La Tana")
    print("="*52)
    try:
        token = getpass.getpass("Incolla il token Airtable e premi Invio: ").strip()
    except Exception:
        token = input("Token Airtable: ").strip()
    if not token:
        print("Nessun token. Esco."); return

    base_id = find_base(token)
    if not base_id: return
    print("Base: %s\n" % base_id)

    print("[1/2] Tabella 'Categorie'")
    cat_id = create_table(token, base_id, "Categorie", [
        {"name":"Nome","type":"singleLineText"},
        {"name":"Sottotitolo","type":"singleLineText"},
        {"name":"Visibile","type":"checkbox","options":{"icon":"check","color":"greenBright"}},
        {"name":"Ordine","type":"number","options":{"precision":0}},
    ])
    if cat_id:
        if table_has_rows(token, base_id, cat_id):
            print("  Ha gia' righe: non inserisco doppioni.")
        else:
            recs = [{"fields":{"Nome":n,"Sottotitolo":s,"Visibile":True,"Ordine":o}}
                    for (n,s,o) in CATEGORIE]
            print("  Inserite:", insert(token, base_id, cat_id, recs), "categorie.")

    print("\n[2/2] Tabella 'Testi sito'")
    txt_id = create_table(token, base_id, "Testi sito", [
        {"name":"Chiave","type":"singleLineText"},
        {"name":"Etichetta","type":"singleLineText"},
        {"name":"Testo","type":"multilineText"},
        {"name":"Ordine","type":"number","options":{"precision":0}},
    ])
    if txt_id:
        if table_has_rows(token, base_id, txt_id):
            print("  Ha gia' righe: non inserisco doppioni.")
        else:
            recs = [{"fields":{"Chiave":k,"Etichetta":e,"Testo":t,"Ordine":o}}
                    for (k,e,t,o) in TESTI]
            print("  Inseriti:", insert(token, base_id, txt_id, recs), "testi.")

    print("\n" + "="*52)
    print(" FATTO. Ora lancia il workflow su GitHub.")
    print("="*52)


if __name__ == "__main__":
    main()
