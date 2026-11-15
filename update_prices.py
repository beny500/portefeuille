"""Met à jour prices.json avec les derniers cours (Yahoo Finance), convertis en EUR."""
import json,re,time,datetime,urllib.parse,urllib.request
H={"User-Agent":"Mozilla/5.0"}
CC={"FR":".PA","DE":".DE","NL":".AS","BE":".BR","IT":".MI","DK":".CO","LU":".DE"}
def get(u):
    for i in range(3):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=20))
        except Exception: time.sleep(2*(i+1))
def quote(sym):
    d=get("https://query1.finance.yahoo.com/v8/finance/chart/"+urllib.parse.quote(sym)+"?range=5d&interval=1d")
    try:
        m=d["chart"]["result"][0]["meta"]; return m["regularMarketPrice"],m["currency"]
    except Exception: return None
def resolve(isin):
    d=get("https://query1.finance.yahoo.com/v1/finance/search?q="+isin+"&quotesCount=8&newsCount=0") or {}
    q=[x["symbol"] for x in d.get("quotes",[]) if x.get("quoteType") in ("EQUITY","ETF")]
    suf=CC.get(isin[:2])
    for s in q:
        if (suf and s.endswith(suf)) or (not suf and "." not in s): return s
    return q[0] if q else None
FX={}
def to_eur(v,c):
    if c=="GBp": v,c=v/100,"GBP"
    if c=="EUR": return v
    if c not in FX:
        r=quote("EUR"+c+"=X"); FX[c]=r[0] if r else None
    return v/FX[c] if FX[c] else None
sym=json.load(open("symbols.json")); pr=json.load(open("prices.json")); bad=[]
for i in list(pr["prices"]):
    if i not in sym:
        s=resolve(i) if re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}[0-9]",i) else i
        if s: sym[i]=s
    q=quote(sym[i]) if i in sym else None
    e=to_eur(*q) if q else None
    if e: pr["prices"][i]=round(e,4)
    else: bad.append(i)
pr["asof"]=datetime.date.today().isoformat()
json.dump(pr,open("prices.json","w"),indent=0); json.dump(sym,open("symbols.json","w"),indent=0,sort_keys=True)
print("Sans cours (ancien cours conservé):",bad)
