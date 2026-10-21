# -*- coding: utf-8 -*-
"""
Monta as 3 paginas do site a partir de um modelo so (2026-10-21): index.html (portugues), en/index.html e ar/index.html.
  fonte/modelo.html  o HTML com {{chave}} no lugar dos textos; <!--so:pt-->...<!--/so--> fica so nas linguas da lista;
  fonte/textos.json  os textos de cada lingua; "_pagina" (titulo, enderecos, pastas das midias), "_uses" e "_cfg" (as abas e as
                     opcoes do "Troque na hora", que o app.js le do bloco i18n de cada pagina).
Mudou o layout? Muda o modelo. Mudou um texto? Muda o textos.json (nas 3 linguas). Depois rode e confira.
Uso (na pasta do site): python fonte/montar.py
Esperado: [MontaSite] OK ...
"""
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LINGUAS = {"pt": "index.html", "en": os.path.join("en", "index.html"), "ar": os.path.join("ar", "index.html")}
ROTULO = {"pt": "PT", "en": "EN", "ar": "عربي"}
CAMINHO = {"pt": "", "en": "en/", "ar": "ar/"}


def links_lingua(atual, raiz):
    partes = []
    for lg in ("pt", "en", "ar"):
        extra = ' lang="ar"' if lg == "ar" else ""
        atributo = ' aria-current="page"' if lg == atual else ""
        partes.append('<a href="%s" hreflang="%s"%s%s>%s</a>' % ((raiz + CAMINHO[lg]) or "./", "pt-BR" if lg == "pt" else lg, extra, atributo, ROTULO[lg]))
    return "".join(partes)


def montar(modelo, textos, lg):
    t = dict(textos[lg])
    pg = t.pop("_pagina")
    uses, cfg, ill = t.pop("_uses"), t.pop("_cfg"), t.pop("_ill")
    v = {}
    v.update(t)
    v.update(pg)
    v["og_media"] = pg["media"].replace("../", "")
    v["lang_links"] = links_lingua(lg, pg["root"])
    v["use_t"], v["use_d"] = uses["captacao"]
    v["cfg_cap0"] = cfg["estilo"][0][2] + ill
    v["cfg_alt0"] = cfg["estilo"][0][3]
    v["i18n"] = json.dumps({"uses": uses, "cfg": cfg, "ill": ill, "media": pg["media"]}, ensure_ascii=False).replace("</", "<\\/")
    html = re.sub(r"<!--so:([a-z,]+)-->(.*?)<!--/so-->", lambda m: m.group(2) if lg in m.group(1).split(",") else "", modelo, flags=re.S)
    for _ in range(2):                          # 2 passadas: um texto pode trazer {{privacy}} ou {{root}}
        html = re.sub(r"{{(\w+)}}", lambda m: v[m.group(1)] if m.group(1) in v else m.group(0), html)
    falta = sorted(set(re.findall(r"{{(\w+)}}", html)))
    if falta:
        raise SystemExit("[MontaSite] ERRO: sem texto para %s em %s" % (falta, lg))
    return html


def main():
    modelo = open(os.path.join(RAIZ, "fonte", "modelo.html"), encoding="utf-8").read()
    textos = json.load(open(os.path.join(RAIZ, "fonte", "textos.json"), encoding="utf-8"))
    chaves = {lg: set(textos[lg]) for lg in textos}
    if chaves["pt"] != chaves["en"] or chaves["pt"] != chaves["ar"]:
        raise SystemExit("[MontaSite] ERRO: as linguas tem chaves diferentes: %s" % sorted((chaves["pt"] ^ chaves["en"]) | (chaves["pt"] ^ chaves["ar"])))
    feitos = []
    for lg, saida in LINGUAS.items():
        html = montar(modelo, textos, lg)
        caminho = os.path.join(RAIZ, saida)
        os.makedirs(os.path.dirname(caminho) or RAIZ, exist_ok=True)
        open(caminho, "w", encoding="utf-8", newline="\n").write(html)
        feitos.append("%s %d KB" % (saida.replace(os.sep, "/"), len(html.encode("utf-8")) // 1024))
    print("[MontaSite] OK " + "; ".join(feitos))


main()
