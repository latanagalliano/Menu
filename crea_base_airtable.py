#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 Crea la tabella "Piatti" su Airtable — La Tana
============================================================
PRIMA di lanciarlo:
  - Crea a mano una base VUOTA chiamata esattamente:  Menu La Tana
  - Il token deve avere accesso a QUELLA base, con gli scope:
      schema.bases:read, schema.bases:write,
      data.records:read, data.records:write

Come lanciarlo su Colab (da telefono):
     import urllib.request
     code = urllib.request.urlopen("https://raw.githubusercontent.com/latanagalliano/Menu/main/crea_base_airtable.py").read().decode()
     exec(code)

!! ALLERGENI: sono una PROPOSTA basata sugli ingredienti.
   VANNO VERIFICATI CON LA CUCINA prima di andare online.
============================================================
"""

import json, sys, time, getpass
import urllib.request, urllib.error

API = "https://api.airtable.com/v0"
BASE_NAME = "Menu La Tana"
TABLE_NAME = "Piatti"

ALLERGENI = ["Glutine","Crostacei","Uova","Pesce","Arachidi","Soia","Latte",
             "Frutta a guscio","Sedano","Senape","Sesamo","Solfiti","Lupini","Molluschi"]

KEY2LABEL = {
    "glutine":"Glutine","crostacei":"Crostacei","uova":"Uova","pesce":"Pesce",
    "arachidi":"Arachidi","soia":"Soia","latte":"Latte","frutta":"Frutta a guscio",
    "sedano":"Sedano","senape":"Senape","sesamo":"Sesamo","solfiti":"Solfiti",
    "lupini":"Lupini","molluschi":"Molluschi"
}

CATEGORIE = ["Antipasti","Primi","Contorni","Pizze","Aggiunte","Birre","Vini","Bevande"]

# (categoria, nome, descrizione, prezzo, surgelato, [allergeni])
PIATTI = [
 ("Antipasti","Crostini","","€ 4,50",False,["glutine","latte","pesce","sedano"]),
 ("Antipasti","Antipasto di Mare","","€ 10",True,["pesce","crostacei","molluschi","sedano"]),
 ("Antipasti","Antipasto Toscano","","€ 10",False,["glutine","latte","pesce","sedano","solfiti"]),
 ("Antipasti","Antipasto di Verdure Sott'Olio","","€ 6",False,["solfiti"]),

 ("Primi","Spaghetti alla Carrettiera","","€ 7",False,["glutine"]),
 ("Primi","Penne ai Medici","","€ 8",False,["glutine","latte"]),
 ("Primi","Penne Stracciate","","€ 8",False,["glutine","latte"]),
 ("Primi","Penne Funghi e Salsiccia","","€ 9,50",True,["glutine","latte","solfiti"]),
 ("Primi","Tortelli al Ragù","","€ 10",True,["glutine","uova","latte","sedano"]),
 ("Primi","Tortelli Burro e Salvia","","€ 9,50",True,["glutine","uova","latte"]),
 ("Primi","Spaghetti al Granchio","","€ 10",True,["glutine","crostacei","sedano"]),
 ("Primi","Tagliatelle ai Funghi Porcini","","€ 10",True,["glutine","uova","latte"]),
 ("Primi","Würstel con Patate Fritte","","€ 9",True,["latte","soia"]),
 ("Primi","Salsiccia con Patate o Fagioli","","€ 10",False,["solfiti"]),

 ("Contorni","Patate Fritte","","€ 4",True,[]),
 ("Contorni","Insalata Verde","","€ 3",False,[]),
 ("Contorni","Insalata Mista","","€ 5",False,[]),

 ("Pizze","Margherita","pomodoro e mozzarella","€ 6,50",False,["glutine","latte"]),
 ("Pizze","Capricciosa","pomodoro, mozzarella, prosciutto cotto e funghi","€ 8",False,["glutine","latte"]),
 ("Pizze","Quattro Stagioni","pomodoro, mozzarella, prosciutto cotto, funghi, carciofi e olive","€ 8",False,["glutine","latte"]),
 ("Pizze","Frutti di Mare","pomodoro, mozzarella e frutti di mare","€ 10",True,["glutine","latte","pesce","crostacei","molluschi"]),
 ("Pizze","Galliano","pomodoro, mozzarella, funghi e salsiccia","€ 8",False,["glutine","latte","solfiti"]),
 ("Pizze","Fantasia","pomodoro, mozzarella, un po' di tutto","€ 8,50",False,["glutine","latte"]),
 ("Pizze","La Tana","pomodoro, mozzarella, würstel, olive e carciofi","€ 8",False,["glutine","latte","soia"]),
 ("Pizze","Vesuvio","pomodoro, mozzarella e prosciutto cotto","€ 7,50",False,["glutine","latte"]),
 ("Pizze","La Diavola","pomodoro, mozzarella, salsiccia e peperoncino","€ 7,50",False,["glutine","latte","solfiti"]),
 ("Pizze","Tonno","pomodoro, mozzarella e tonno","€ 7,50",False,["glutine","latte","pesce"]),
 ("Pizze","Funghi","pomodoro, mozzarella e funghi champignon","€ 7",False,["glutine","latte"]),
 ("Pizze","Gorgonzola","pomodoro, mozzarella e gorgonzola","€ 8",False,["glutine","latte"]),
 ("Pizze","Quattro Formaggi","pomodoro, mozzarella, gorgonzola, stracchino ed edamer","€ 8,50",False,["glutine","latte"]),
 ("Pizze","Contadina","pomodoro, mozzarella, prosciutto cotto e cipolle","€ 8",False,["glutine","latte"]),
 ("Pizze","Marinara","pomodoro, aglio e origano","€ 5,50",False,["glutine"]),
 ("Pizze","Vegetariana","pomodoro, mozzarella, funghi, cipolle, olive e verdure","€ 8,50",False,["glutine","latte"]),
 ("Pizze","Porcini","pomodoro, mozzarella e funghi porcini","€ 9",True,["glutine","latte"]),
 ("Pizze","Gorgonzola e Speck","pomodoro, mozzarella, gorgonzola e speck","€ 9,50",False,["glutine","latte"]),
 ("Pizze","Maialona","pomodoro, mozzarella, prosciutto cotto, salsiccia e würstel","€ 8,50",False,["glutine","latte","soia","solfiti"]),
 ("Pizze","Donatello","pomodoro, mozzarella, melanzane e cipolle","€ 8",False,["glutine","latte"]),
 ("Pizze","Napoli","pomodoro, mozzarella, acciughe, capperi e olive","€ 7",False,["glutine","latte","pesce"]),
 ("Pizze","Calabrese","pomodoro, mozzarella, salamino e cipolla","€ 8",False,["glutine","latte","solfiti"]),
 ("Pizze","Toscana","pomodoro, mozzarella, melanzane e salsiccia","€ 8,50",False,["glutine","latte","solfiti"]),
 ("Pizze","Siciliana","pomodoro, acciughe, capperi e olive","€ 6,50",False,["glutine","pesce"]),
 ("Pizze","Strega","porri, cipolla e peperoncino","€ 7,50",False,["glutine"]),
 ("Pizze","Burrata, Acciughe e Capperi","burrata, acciughe e capperi","€ 9",False,["glutine","latte","pesce"]),
 ("Pizze","N'duja e Scamorza","n'duja e scamorza","€ 8,50",False,["glutine","latte"]),
 ("Pizze","Calzone","mozzarella e prosciutto cotto","€ 8",False,["glutine","latte"]),
 ("Pizze","Calzone Farcito","mozzarella e un po' di tutto","€ 8,50",False,["glutine","latte"]),
 ("Pizze","Covaccino all'Olio","schiacciatina all'olio","€ 8",False,["glutine"]),
 ("Pizze","Covaccino","schiacciatina con prosciutto crudo","€ 7",False,["glutine"]),
 ("Pizze","Covaccino con Mozzarella","schiacciatina con mozzarella e prosciutto cotto","€ 8",False,["glutine","latte"]),
 ("Pizze","Covaccino Estivo","schiacciatina con pomodoro, prosciutto e rucola","€ 8",False,["glutine"]),
 ("Pizze","Covaccino Estivo con Mozzarella","schiacciatina con mozzarella, prosciutto e rucola","€ 8,50",False,["glutine","latte"]),
 ("Pizze","Covaccino Porcini e Speck","schiacciatina con mozzarella, porcini e speck","€ 9,50",True,["glutine","latte"]),

 ("Aggiunte","Prosciutto Crudo","","€ 2,50",False,[]),
 ("Aggiunte","Mozzarella di Bufala","","€ 2",False,["latte"]),
 ("Aggiunte","Rucola","","€ 0,50",False,[]),
 ("Aggiunte","Burrata","","€ 3",False,["latte"]),
 ("Aggiunte","Altri ingredienti","secondo quantità","",False,[]),

 ("Birre","Franziskaner 0,5 L","","€ 4",False,["glutine"]),
 ("Birre","Ceres 0,4 L","","€ 3,50",False,["glutine"]),
 ("Birre","Media alla Spina 0,5 L","","€ 5",False,["glutine"]),
 ("Birre","Piccola alla Spina 0,25 L","","€ 3",False,["glutine"]),
 ("Birre","Moretti 0,66 L","","€ 3,50",False,["glutine"]),
 ("Birre","Borgo al Cornio 0,75 L","artigianale","€ 10",False,["glutine"]),

 ("Vini","Vino della Casa 1 L","","€ 10",False,["solfiti"]),
 ("Vini","Vino della Casa 0,5 L","","€ 5",False,["solfiti"]),
 ("Vini","Vino Bianco Frizzante alla Spina 1 L","","€ 10",False,["solfiti"]),
 ("Vini","Vino Bianco Frizzante alla Spina 0,5 L","","€ 5",False,["solfiti"]),
 ("Vini","Vino in Bottiglia","","€ 5",False,["solfiti"]),

 ("Bevande","Coca Cola Media alla Spina","","€ 4,50",False,[]),
 ("Bevande","Coca Cola Piccola alla Spina","","€ 2,50",False,[]),
 ("Bevande","Lattine","","€ 2,50",False,[]),
 ("Bevande","Acqua Minerale 1 L","","€ 2,50",False,[]),
 ("Bevande","Acqua Minerale 0,5 L","","€ 1,50",False,[]),
 ("Bevande","Amari","","€ 2,50",False,["solfiti"]),
 ("Bevande","Caffè","","€ 1,50",False,[]),
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


def main():
    print("="*52)
    print(" Setup base Airtable — La Tana")
    print("="*52)
    try:
        token = getpass.getpass("Incolla il token Airtable e premi Invio: ").strip()
    except Exception:
        token = input("Token Airtable: ").strip()
    if not token:
        print("Nessun token. Esco."); return

    print("\n[1/3] Cerco la base '%s'..." % BASE_NAME)
    st, res = req("GET", API + "/meta/bases", token)
    if st != 200:
        print("  ERRORE (%s): %s" % (st, res))
        print("  Il token ha lo scope 'schema.bases:read'?"); return
    bases = res.get("bases", [])
    base_id = None
    for b in bases:
        if b.get("name","").strip() == BASE_NAME:
            base_id = b["id"]; break
    if not base_id:
        if len(bases) == 1:
            base_id = bases[0]["id"]
            print("  Nome diverso, ma il token vede una sola base ('%s'): uso quella." % bases[0].get("name"))
        else:
            print("  Base '%s' non trovata. Basi visibili dal token:" % BASE_NAME)
            for b in bases: print("    -", b.get("name"), b["id"])
            print("  Crea la base (o aggiungila al token), poi rilancia."); return
    print("  Trovata: %s" % base_id)

    print("\n[2/3] Creo la tabella '%s'..." % TABLE_NAME)
    fields = [
        {"name":"Nome","type":"singleLineText"},
        {"name":"Descrizione","type":"multilineText"},
        {"name":"Prezzo","type":"singleLineText"},
        {"name":"Categoria","type":"singleSelect","options":{"choices":[{"name":c} for c in CATEGORIE]}},
        {"name":"Allergeni","type":"multipleSelects","options":{"choices":[{"name":a} for a in ALLERGENI]}},
        {"name":"Surgelato","type":"checkbox","options":{"icon":"check","color":"yellowBright"}},
        {"name":"Visibile","type":"checkbox","options":{"icon":"check","color":"greenBright"}},
        {"name":"Ordine","type":"number","options":{"precision":0}},
    ]
    st, res = req("POST", API + "/meta/bases/%s/tables" % base_id, token,
                  {"name":TABLE_NAME,"fields":fields})
    if st == 200:
        table_id = res["id"]; print("  Creata: %s" % table_id)
    elif st == 422 and "DUPLICATE" in json.dumps(res).upper():
        st2, res2 = req("GET", API + "/meta/bases/%s/tables" % base_id, token)
        table_id = None
        for t in res2.get("tables", []):
            if t.get("name") == TABLE_NAME: table_id = t["id"]; break
        if not table_id:
            print("  ERRORE: %s" % res); return
        print("  Esisteva gia': la riuso (%s)." % table_id)
    else:
        print("  ERRORE (%s): %s" % (st, res))
        print("  Serve lo scope 'schema.bases:write'."); return

    print("\n[3/3] Inserisco i %d piatti..." % len(PIATTI))
    records = []
    for i,(cat,nome,desc,prezzo,frozen,keys) in enumerate(PIATTI, start=1):
        records.append({"fields":{
            "Nome":nome, "Descrizione":desc, "Prezzo":prezzo, "Categoria":cat,
            "Allergeni":[KEY2LABEL[k] for k in keys],
            "Surgelato":bool(frozen), "Visibile":True, "Ordine":i
        }})
    ok = 0
    for i in range(0, len(records), 10):
        st, res = req("POST", API + "/%s/%s" % (base_id, table_id), token,
                      {"records":records[i:i+10], "typecast":True})
        if st == 200:
            ok += len(res.get("records", [])); print("  ...%d/%d" % (ok, len(records)))
        else:
            print("  ERRORE inserimento (%s): %s" % (st, res))
            print("  Serve lo scope 'data.records:write'."); return
        time.sleep(0.25)

    print("\n" + "="*52)
    print(" FATTO. %d piatti inseriti." % ok)
    print(" base_id: %s" % base_id)
    print(" >> SEGNATELO: serve per il secret AIRTABLE_BASE_ID su GitHub.")
    print("="*52)


if __name__ == "__main__":
    main()
