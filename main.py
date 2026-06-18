import json, os, random, sys, datetime, math
import pygame as pg

W, H = 1152, 648
FPS  = 60
BASE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE, "assets")
DATA   = os.path.join(BASE, "data")

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GREY  = (120, 120, 120)
RED   = (220,  70,  65)
GREEN = ( 80, 200, 100)

GIVERS  = ["associate","acquaintance","employer","former colleague","supplier",
           "handler","distant relative","contact","client","informant"]
MOTIVES = ["safekeeping","payment-in-kind","trade","debt settlement",
           "coercion","bribe","insurance","blackmail"]
PLACES  = ["the canal footbridge","rear of depot 9","the civic archive loading bay",
           "transit hub sub-level B","the laundrette on Weld Street",
           "parking structure level 4","the overnight market on Cress Lane",
           "platform 11 east rail","the maintenance corridor under district hall"]
QUESTIONS = [("who","who gave it?"),("where","where from?"),("why","why have it?"),
             ("how","how long?"),("know","know them well?"),("verify","who can verify?"),
             ("evidence","explain evidence?"),("used","ever use it?")]

# helper funcs

def jload(f, d):
    try:
        with open(os.path.join(DATA, f), encoding="utf-8") as fp: return json.load(fp)
    except: return d

def initials(n): return ".".join(p[0] for p in n.split()) + "."

def wrap(text, font, w): # stack overflow helped a lot with this, it was funky
    words, lines, cur = str(text).split(), [], ""
    for word in words:
        t = word if not cur else cur + " " + word
        if font.size(t)[0] <= w: cur = t
        else:
            if cur: lines.append(cur)
            cur = word
    if cur: lines.append(cur)
    return lines

def blit_wrap(surf, text, x, y, font, col, max_w, max_lines=99):
    lh = font.get_height() + 3
    for i, ln in enumerate(wrap(text, font, max_w)):
        if i >= max_lines: break
        surf.blit(font.render(ln, True, col), (x, y)); y += lh
    return y

def make_fonts():
    mono = pg.font.match_font("consolas,couriernew,lucidaconsole,courier,monospace")
    def f(s, b=False):
        fo = pg.font.Font(mono, s); fo.set_bold(b); return fo
    return {"big": f(40,True), "med": f(22,True), "body": f(16), "sm": f(13), "xs": f(11)}

#  button ui here
def btn(surf, font, x, y, w, h, text, mouse, active=False, danger=False, dim=False):
    r = pg.Rect(x, y, w, h)
    hover = r.collidepoint(mouse)
    if dim:      col, bw = GREY, 1
    elif danger: col, bw = RED,  2 if hover else 1
    elif active or hover: col, bw = WHITE, 2
    else:        col, bw = GREY, 1
    pg.draw.rect(surf, BLACK, r)
    pg.draw.rect(surf, col,   r, bw)
    img = font.render(text, True, col)
    surf.blit(img, img.get_rect(center=r.center))
    return r

# rudimentary case generator

def pick(used, names):
    f, l = names.get("first",["Alex","Sam","Jo"]), names.get("last",["Vale","Cross","Maren"]) # old placeholders....
    for _ in range(400):
        n = random.choice(f)+" "+random.choice(l)
        if n not in used: used.append(n); return n
    n = "X-"+str(len(used)); used.append(n); return n

def person(used, names, jobs, role):
    return {"name":pick(used,names),"role":role,"job":random.choice(jobs),
            "tail":str(random.randint(1000,9999)),
            "record":random.choice(["no prior record","minor fine","unverified warning","sealed file"]),
            "note":random.choice(["moves irregularly","changed address twice","flagged for inconsistency","works unusual hours"])}

def new_case(): # i have the jsons set up now, but i fear if i get rid of these placeholders everything will go kaput
    names = jload("names.json",{"first":["Alex","Sam","Jo"],"last":["Vale","Cross","Maren"]}) # so here they stay
    jobs  = jload("occupations.json",["courier","clerk","inspector","archivist"]) # it's probably fine
    pers  = jload("personalities.json",["Nervous","Dishonest","Honest","Calm"]) # but we ball
    objs  = jload("objects.json",[{"name":"Unlicensed Handgun","category":"Weapon",
        "description":"Pistol, serial filed off.","risk_level":"High","legality":"Illegal",
        "known_suppliers":["black market"],"incidents":["prior robbery scene"]}])
    cols  = [("blue",(88,162,214)),("green",(88,180,104)),("pink",(212,110,162)),
             ("orange",(212,138,58)),("purple",(148,108,200)),("teal",(68,178,168))]
    used  = []
    obj   = random.choice(objs)
    cname, crgb = random.choice(cols)
    s = {"name":pick(used,names),"rgb":crgb,"job":random.choice(jobs),
         "age":random.randint(19,62),"personality":random.choice(pers),
         "record":random.choice(["no prior record","minor fine","questioned — released"])}
    giver  = person(used,names,jobs,random.choice(GIVERS))
    fake   = person(used,names,jobs,random.choice([g for g in GIVERS if g!=giver["role"]]))
    others = [person(used,names,jobs,random.choice(GIVERS)) for _ in range(3)]
    motive = random.choice(MOTIVES)
    fmot   = random.choice([m for m in MOTIVES if m!=motive])
    place  = random.choice(PLACES)
    fplace = random.choice([p for p in PLACES if p!=place])
    today  = datetime.date.today()
    rday   = today - datetime.timedelta(days=random.randint(4,21))
    fday   = rday  + datetime.timedelta(days=random.choice([-3,3,4]))
    ref    = "OP-{:04d}".format(random.randint(1000,9999))
    bio    = "BIO-{:05d}".format(random.randint(10000,99999))
    pfx    = "{:03d}-{:03d}".format(random.randint(100,999),random.randint(100,999))
    people = [giver,fake]+others; random.shuffle(people)
    ev = [
        {"id":"incident",   "label":"INCIDENT REPORT",    "text":f"{s['name']}, {s['age']}yr, {s['job']}. Item: {obj['name']} ({obj['legality']}). Record: {s['record']}. Source unknown."},
        {"id":"msg",        "label":"MESSAGE EXTRACT",     "text":f"From {s['name']}'s phone. Excerpt: '...sign as {initials(giver['name'])} on the form.' Sender ends -{giver['tail']}. Cross-ref phone registry."},
        {"id":"phone",      "label":"PHONE REGISTRY",      "text":f"Number -{giver['tail']} registered to {giver['name']}, {giver['job']}. Combine with message extract."},
        {"id":"cctv",       "label":"CCTV FRAGMENT",       "text":f"At {place} on {rday}: Individual A matches {giver['job']}, name unconfirmed. Individual B matches {s['name']}. Cross-ref employment file."},
        {"id":"employment", "label":"EMPLOYMENT FILE",     "text":f"{giver['name']}, {giver['job']}. Phone ends -{giver['tail']}. Record: {giver['record']}. Note: {giver['note']}. Use with CCTV to confirm presence."},
        {"id":"prints",     "label":"FORENSIC PRINTS",     "text":f"Prints on {obj['name']}: donor ref {bio}. Confidence HIGH. Run {bio} against biometric registry."},
        {"id":"biometric",  "label":"BIOMETRIC REGISTRY",  "text":f"Ref {bio}: {giver['name']}, {giver['job']}. Combine with forensic prints to confirm they handled the item."},
        {"id":"alibi",      "label":f"ALIBI — {fake['name']}","text":f"{fake['name']} claims checkpoint 4 north district all day on {rday}. Gate log confirmed. Could NOT be at {place} that day."},
        {"id":"associates", "label":"ASSOCIATE NETWORK",   "text":f"{s['name']}'s contacts: {', '.join(p['name'] for p in people[:3])}. Both {giver['name']} and {fake['name']} flagged as persons of interest."},
        {"id":"finance",    "label":"FINANCIAL TRACE",     "text":f"{giver['name']} withdrew £{random.randint(200,4000):,} on {rday} near {place}. Memo: 'services rendered'. Motive: {motive}."},
    ]
    contra = [
        ("who",      ["msg","phone"],       f"Suspect named {fake['name']}. But message sender is {initials(giver['name'])} and that number belongs to {giver['name']}."),
        ("where",    ["cctv","employment"], f"Suspect claims {fplace}. CCTV shows someone with job '{giver['job']}' at {place} with suspect. That is {giver['name']}."),
        ("verify",   ["alibi"],             f"Suspect said ask {fake['name']}. Alibi statement proves {fake['name']} was at checkpoint 4 all day — not at {place}."),
        ("know",     ["associates"],        f"Suspect downplayed knowing {giver['name']}. Associate network shows direct link; both flagged as persons of interest."),
        ("how",      ["finance"],           f"Financial trace: {giver['name']} withdrew cash near {place} on exactly {rday}. Timeline inconsistent."),
        ("evidence", ["prints","biometric"],f"Prints ref {bio} on the item. Biometric registry: {bio} belongs to {giver['name']}."),
    ]
    options = list(people)+[{"name":"Unknown — unregistered person","role":"unknown",
                              "job":"unknown","record":"no record","note":"","tail":""}]
    random.shuffle(options)
    return {"ref":ref,"object":obj,"suspect":s,"giver":giver,"fake":fake,
            "motive":motive,"fmot":fmot,"place":place,"fplace":fplace,
            "rday":str(rday),"fday":str(fday),"people":people,
            "evidence":ev,"contra":contra,"options":options,"bio":bio,
            "report":f"{s['name']} found with {obj['name']} ({obj['legality']}). Source unknown."}

def new_game():
    c = new_case()
    return {"case":c,"talk":c["report"],"asked":set(),"found":set(),
            "log":[c["report"]],"notes":"","statements":{},"contradictions":[],
            "active_ev":None,"tab":"case","query":"","page":0,
            "notes_open":False,"notes_tab":"log","notes_typing":False,"log_page":0,
            "picked":None,"verdict":None}


# dialogue, it's not the best but i don't have a lot of time so this is what we are rolling with

def ask(game, qid):
    c,s,g,fk = game["case"],game["case"]["suspect"],game["case"]["giver"],game["case"]["fake"]
    mode = {"dishonest":"lie","cocky":"lie","aggressive":"lie",
            "honest":"truth","friendly":"truth","nervous":"mis"}.get(s["personality"].lower(),"def")
    aev = next((e["label"] for e in c["evidence"] if e["id"]==game["active_ev"]),None)
    lie  = {"who":f"it was {fk['name']}.","where":f"we met at {c['fplace']}.","why":f"a {c['fmot']}.","how":f"since {c['fday']}.","know":f"i barely know {g['name']}.","verify":f"ask {fk['name']}.","evidence":f"{aev or 'that'} proves nothing.","used":"i never used it."}
    tru  = {"who":f"it was {g['name']}.","where":f"at {c['place']}.","why":f"a {c['motive']}.","how":f"since {c['rday']}.","know":f"yes, i know {g['name']}.","verify":f"{g['name']} can confirm.","evidence":"that's consistent with what i said.","used":"no, never."}
    mis  = {"who":f"i think {fk['name']}? not certain.","where":f"near {c['fplace']} i think.","why":f"a {c['motive']} i believe.","how":f"around {c['fday']} maybe.","know":"we've crossed paths.","verify":f"try {fk['name']}...","evidence":"not sure what that shows.","used":"i don't think so."}
    dfl  = {"who":"someone gave it. it's complicated.","where":"a location. does it matter?","why":"people give things.","how":"hard to say.","know":"i know a lot of people.","verify":"i'd rather not involve others.","evidence":f"{aev or 'evidence'} can be read many ways.","used":"i'd rather not answer."}
    base = {"lie":lie,"truth":tru,"mis":mis,"def":dfl}[mode].get(qid,"i have nothing to add.")
    p = s["personality"].lower()
    flavour = {"nervous":"i... {l} i think.","aggressive":"{l} that's final.","friendly":"of course — {l}","cocky":"{l} next question.","paranoid":"why do you ask? {l}"}
    line = flavour.get(p,"{l}").format(l=base)
    game["talk"] = line
    game["asked"].add(qid)
    game["statements"][qid] = line
    game["log"].append(f"[asked: {qid}]  {line}")
    game["active_ev"] = None
    for q,evs,txt in c["contra"]:
        if q in game["asked"] and all(e in game["found"] for e in evs):
            if txt not in game["contradictions"]:
                game["contradictions"].append(txt)
                game["log"].append(f"[CONTRADICTION]  {txt}")

def review(game, ev_id):
    for ev in game["case"]["evidence"]:
        if ev["id"] == ev_id:
            game["found"].add(ev_id); game["active_ev"] = ev_id
            game["log"].append(f"[reviewed]  {ev['label']}")
            ask(game, "_trigger")   # re-check
            game["log"] = [l for l in game["log"] if not l.startswith("[asked: _trigger]")]
            game["statements"].pop("_trigger", None)
            game["asked"].discard("_trigger")
            return ev

# databse rows
def db_rows(game):
    c, tab = game["case"], game["tab"]
    rows = []
    if tab == "case":
        rows = [{"label":"INITIAL REPORT","text":c["report"],"ev":None}]
        rows += [{"label":f"STATEMENT [{k}]","text":v,"ev":None} for k,v in game["statements"].items()]
        rows += [{"label":"CONTRADICTION","text":t,"ev":None} for t in game["contradictions"]]
    elif tab == "people":
        rows = [{"label":f"{p['name']} — {p['role']}","text":f"{p['job']}. {p['record']}. {p['note']}.","ev":None} for p in c["people"]]
    elif tab == "item":
        obj = c["object"]
        rows = [{"label":obj["name"],"text":f"{obj['description']} Risk: {obj['risk_level']}. {obj['legality']}.","ev":None},
                {"label":"KNOWN SUPPLIERS","text":", ".join(obj["known_suppliers"]),"ev":None},
                {"label":"PRIOR INCIDENTS","text":". ".join(obj["incidents"]),"ev":None}]
    elif tab == "evidence":
        rows = [{"label":e["label"],"text":e["text"],"ev":e["id"]} for e in c["evidence"]]
    q = game["query"].lower()
    if q: rows = [r for r in rows if q in (r["label"]+r["text"]).lower()]
    return rows

# game scenes

PAPER  = pg.Rect(255,318,390,248) # the coordinates were being so weird for so long,
SUSP   = pg.Rect(340, 55,380,315) # there's probably some magic better way but this works 
STRIP  = 210   # height for strip

def draw_menu(surf, fonts, mouse, session):
    surf.fill(BLACK); cx = W//2; clicks = []
    y = 140
    surf.blit(fonts["big"].render("ORIGIN PENDING", True, WHITE),
              fonts["big"].render("ORIGIN PENDING",True,WHITE).get_rect(centerx=cx,top=y))
    y += 72
    for line,col in [("An interrogation game.",GREY),("",WHITE),
                     ("Review the suspects, find out who gave the object.",WHITE),
                     ("Look through evidence and statements'",WHITE),
                     ("Find links between evidence and suspects.",WHITE),
                     ("",WHITE),("Suspects may or may not tell the truth.",GREY)]:
        if line:
            img = fonts["sm"].render(line,True,col)
            surf.blit(img, img.get_rect(centerx=cx,top=y))
        y += 26
    if session["right"] or session["wrong"]:
        t = f"record:  {session['right']} correct   {session['wrong']} wrong   streak {session['streak']}"
        img = fonts["xs"].render(t,True,GREY); surf.blit(img, img.get_rect(centerx=cx,top=y+10))
    r1 = btn(surf,fonts["body"],cx-140,y+40,280,46,"START CASE",mouse)
    r2 = btn(surf,fonts["sm"],cx-80,y+98,160,34,"QUIT",mouse)
    clicks += [(r1,"new"),(r2,"quit")]; return clicks

def draw_room(surf, fonts, game, mouse, room_img, susp_img):
    surf.fill(BLACK); clicks = []
    surf.blit(room_img,(0,0)); surf.blit(susp_img,(0,0))
    for area in (PAPER,SUSP):
        if area.collidepoint(mouse):
            ov = pg.Surface((area.w,area.h)); ov.set_alpha(38); ov.fill((255,245,180))
            surf.blit(ov,area.topleft); pg.draw.rect(surf,WHITE,area,1)
    clicks += [(PAPER,"toggle_notes"),(SUSP,"toggle_notes")]

    # i think it looks nice to have this line
    sy = H - STRIP
    pg.draw.rect(surf, BLACK, (0,sy,W,STRIP))
    pg.draw.line(surf, WHITE, (0,sy),(W,sy), 2)

    s = game["case"]["suspect"]
    dlg_w = W - 280
    # dialogue box
    pg.draw.rect(surf, BLACK, (12,sy+10,dlg_w,118))
    pg.draw.rect(surf, WHITE, (12,sy+10,dlg_w,118), 2)
    surf.blit(fonts["sm"].render(f"  {s['name']}  [{s['personality']}]  ",True,WHITE),(22,sy+14))
    pg.draw.line(surf,WHITE,(14,sy+30),(12+dlg_w-2,sy+30),1)
    blit_wrap(surf,game["talk"],22,sy+36,fonts["body"],WHITE,dlg_w-28,max_lines=4)

    # questions
    qw = dlg_w//4 - 4
    for i,(qid,label) in enumerate(QUESTIONS):
        done = qid in game["asked"]
        bx = 12 + (i%4)*(qw+4); by = sy+136+(i//4)*28
        r = btn(surf,fonts["xs"],bx,by,qw,24,("✓ " if done else "")+label,mouse,dim=done)
        clicks.append((r,"ask",qid))

    # right nav
    nx = W-264
    r1 = btn(surf,fonts["sm"],nx,sy+10,252,36,"NOTES"+" [open]"*game["notes_open"],mouse,active=game["notes_open"])
    r2 = btn(surf,fonts["sm"],nx,sy+54,252,36,"DATABASE  →",mouse)
    r3 = btn(surf,fonts["sm"],nx,sy+98,252,36,"FILE VERDICT",mouse,danger=True)
    clicks += [(r1,"toggle_notes"),(r2,"computer"),(r3,"verdict")]
    n = len(game["contradictions"])
    surf.blit(fonts["xs"].render(f"links: {n}",True,RED if n else GREY),(nx+4,sy+146))

    if game["notes_open"]: draw_notes(surf,fonts,game,mouse,clicks)
    return clicks

def draw_notes(surf, fonts, game, mouse, clicks):
    ph = 370; py = (H-STRIP)-ph
    pg.draw.rect(surf,BLACK,(12,py,W-24,ph))
    pg.draw.rect(surf,WHITE,(12,py,W-24,ph),2)
    surf.blit(fonts["sm"].render(f"NOTES — {game['case']['ref']}",True,WHITE),(24,py+8))
    rc = btn(surf,fonts["xs"],W-44,py+6,28,20,"X",mouse)
    clicks.append((rc,"toggle_notes"))
    tx = 16
    for tid,tlabel in [("log","CASE LOG"),("notes","YOUR NOTES"),("contra","CONTRADICTIONS")]:
        tr = btn(surf,fonts["xs"],tx,py+32,148,22,tlabel,mouse,active=game["notes_tab"]==tid)
        clicks.append((tr,"notes_tab",tid)); tx += 152
    pg.draw.line(surf,WHITE,(14,py+58),(W-14,py+58),1)
    cx2,cy,cw2 = 22,py+64,W-48
    if game["notes_tab"] == "log":
        per=10; items=game["log"]; total=max(1,math.ceil(len(items)/per))
        page=game.get("log_page",0); shown=items[page*per:page*per+per]
        surf.blit(fonts["xs"].render(f"page {page+1}/{total}",True,GREY),(cx2,cy)); cy+=16
        for note in shown:
            col=RED if "[CONTRA" in note else (GREEN if "[review" in note else GREY)
            cy=blit_wrap(surf,note,cx2,cy,fonts["xs"],col,cw2,2); cy+=2
        rl=btn(surf,fonts["xs"],cx2,py+ph-26,80,18,"< prev",mouse,dim=page==0)
        rn=btn(surf,fonts["xs"],cx2+86,py+ph-26,80,18,"next >",mouse,dim=(page+1)*per>=len(items))
        clicks+=[(rl,"log_page",-1),(rn,"log_page",1)]
    elif game["notes_tab"] == "notes":
        typing = game["notes_typing"]
        pg.draw.rect(surf,BLACK,(cx2-4,cy,cw2+8,ph-80))
        pg.draw.rect(surf,WHITE if typing else GREY,(cx2-4,cy,cw2+8,ph-80),1)
        surf.blit(fonts["xs"].render("click to type  •  esc to stop",True,GREY),(cx2,cy+3))
        pg.draw.line(surf,GREY,(cx2-4,cy+18),(cx2+cw2+4,cy+18),1)
        d = game["notes"]+("|" if typing and (pg.time.get_ticks()//500)%2==0 else "")
        blit_wrap(surf,d or "...",cx2,cy+22,fonts["sm"],WHITE,cw2,12)
        nr = pg.Rect(cx2-4,cy,cw2+8,ph-80); clicks.append((nr,"focus_notes"))
    elif game["notes_tab"] == "contra":
        if not game["contradictions"]:
            surf.blit(fonts["sm"].render("None found yet.",True,GREY),(cx2,cy)); cy+=24
            blit_wrap(surf,"you can review evidence in the database",cx2,cy,fonts["xs"],GREY,cw2)
        else:
            for i,con in enumerate(game["contradictions"]):
                surf.blit(fonts["xs"].render(f"[{i+1}]",True,RED),(cx2,cy))
                cy=blit_wrap(surf,con,cx2+24,cy,fonts["xs"],WHITE,cw2-28,3)
                pg.draw.line(surf,GREY,(cx2,cy+3),(cx2+cw2,cy+3),1); cy+=8

def draw_database(surf, fonts, game, mouse):
    surf.fill(BLACK); clicks = []
    rb = btn(surf,fonts["sm"],10,10,100,32,"← BACK",mouse); clicks.append((rb,"room"))
    pg.draw.rect(surf,BLACK,(118,10,W-128,32)); pg.draw.rect(surf,WHITE,(118,10,W-128,32),1)
    surf.blit(fonts["sm"].render(f"DATABASE  //  {game['case']['ref']}",True,WHITE),(128,19))
    tx=10
    for tid,tl in [("case","CASE FILE"),("people","PERSONS"),("item","ITEM"),("evidence","EVIDENCE")]:
        r=btn(surf,fonts["sm"],tx,50,136,28,tl,mouse,active=game["tab"]==tid)
        clicks.append((r,"db_tab",tid)); tx+=140
    # search bar
    pg.draw.rect(surf,BLACK,(10,86,W-78,28)); pg.draw.rect(surf,WHITE,(10,86,W-78,28),1)
    q=game["query"]
    surf.blit(fonts["sm"].render(f"> {q}" if q else "> type to filter…",True,WHITE if q else GREY),(18,92))
    rc=btn(surf,fonts["xs"],W-62,86,52,28,"CLEAR",mouse,dim=not q); clicks.append((rc,"db_clear"))
    if game["tab"]=="evidence":
        surf.blit(fonts["xs"].render("Review files here",True,GREY),(12,120))
    # rows are text lists
    rows=db_rows(game); per=5; max_pg=max(0,math.ceil(len(rows)/per)-1)
    game["page"]=min(game["page"],max_pg); page=game["page"]
    shown=rows[page*per:page*per+per]
    start_y=130 if game["tab"]=="evidence" else 122
    avail=H-start_y-40; row_h=max(66,avail//max(1,per)); ry=start_y
    for row in shown:
        reviewed = row["ev"] in game["found"]
        lc = GREEN if reviewed else WHITE
        surf.blit(fonts["sm"].render(row["label"],True,lc),(14,ry+4))
        if reviewed and row["ev"]: surf.blit(fonts["xs"].render("✓ reviewed",True,GREEN),(W-110,ry+6))
        blit_wrap(surf,row["text"],14,ry+22,fonts["xs"],GREY,W-130,max_lines=3)
        if row["ev"] and not reviewed:
            rr=btn(surf,fonts["xs"],W-106,ry+row_h-28,96,20,"REVIEW",mouse)
            clicks.append((rr,"review",row["ev"]))
        pg.draw.line(surf,GREY,(12,ry+row_h-4),(W-12,ry+row_h-4),1); ry+=row_h
    if not rows: surf.blit(fonts["body"].render("No records match.",True,GREY),(16,start_y+14))
    pg.draw.line(surf,WHITE,(10,H-36),(W-10,H-36),1)
    surf.blit(fonts["xs"].render(f"page {page+1}/{max_pg+1}  -  {len(rows)} entries  -  type to filter  -  backspace deletes",True,GREY),(14,H-28))
    rl=btn(surf,fonts["xs"],W-168,H-32,72,22,"< prev",mouse,dim=page==0)
    rn=btn(surf,fonts["xs"],W-90, H-32,72,22,"next >",mouse,dim=page>=max_pg)
    clicks+=[(rl,"db_page",-1),(rn,"db_page",1)]; return clicks

def draw_verdict(surf, fonts, game, mouse):
    surf.fill(BLACK); clicks = []
    rb=btn(surf,fonts["sm"],10,10,100,32,"← BACK",mouse); clicks.append((rb,"room"))
    pg.draw.rect(surf,BLACK,(118,10,W-128,32)); pg.draw.rect(surf,WHITE,(118,10,W-128,32),1)
    surf.blit(fonts["sm"].render("FINAL VERDICT: WHO GAVE THEM THAT?",True,WHITE),(128,19))
    c=game["case"]
    surf.blit(fonts["xs"].render(f"Suspect: {c['suspect']['name']}   Item: {c['object']['name']}   Ref: {c['ref']}",True,GREY),(14,52))
    pg.draw.line(surf,WHITE,(10,68),(W-10,68),1)
    y=76
    for p in c["options"]:
        picked = game["picked"]==p["name"]
        dot=fonts["body"].render("●" if picked else "○",True,WHITE if picked else GREY) # worked well for showing clicks
        surf.blit(dot,(22,y+6))
        surf.blit(fonts["body"].render(p["name"],True,WHITE),(52,y+6))
        surf.blit(fonts["xs"].render(f"{p['role']}  •  {p['job']}  •  {p['record']}",True,GREY),(52,y+28))
        clicks.append((pg.Rect(10,y,W-20,50),"pick",p["name"]))
        pg.draw.line(surf,GREY,(10,y+52),(W-10,y+52),1); y+=58
        if y+50>H-52: break
    ok=bool(game["picked"])
    rs=btn(surf,fonts["body"],W//2-150,H-48,300,38,"SUBMIT VERDICT" if ok else "select a name first",mouse,danger=ok,dim=not ok)
    if ok: clicks.append((rs,"submit"))
    return clicks

def draw_result(surf, fonts, game, mouse, session):
    surf.fill(BLACK); clicks = []
    c=game["case"]; correct=game["verdict"]==c["giver"]["name"]
    col=GREEN if correct else RED; word="CORRECT" if correct else "WRONG"
    img=fonts["big"].render(word,True,col); surf.blit(img,img.get_rect(centerx=W//2,top=20))
    rec=fonts["sm"].render(f"record:  {session['right']} correct   {session['wrong']} wrong   streak {session['streak']}",True,GREY)
    surf.blit(rec,rec.get_rect(centerx=W//2,top=76))
    pg.draw.line(surf,WHITE,(60,104),(W-60,104),1)
    y=112
    for label,val in [("SOURCE",f"{c['giver']['name']}  ({c['giver']['role']}, {c['giver']['job']})"),
                      ("MOTIVE",c["motive"]),("LOCATION",c["place"]),("DATE",c["rday"]),
                      ("ITEM",c["object"]["name"]),("SUSPECT",f"{c['suspect']['name']} — {c['suspect']['personality']}")]:
        surf.blit(fonts["xs"].render(label,True,GREY),(64,y+3))
        surf.blit(fonts["sm"].render(val,True,WHITE),(160,y))
        pg.draw.line(surf,GREY,(60,y+22),(W-60,y+22),1); y+=26
        if y>H-90: break
    if not correct: surf.blit(fonts["sm"].render(f"You named: {game['verdict']}",True,RED),(64,y+4))
    r1=btn(surf,fonts["body"],W//2-180,H-56,170,42,"NEXT CASE",mouse)
    r2=btn(surf,fonts["body"],W//2+10, H-56,170,42,"MAIN MENU",mouse)
    clicks+=[(r1,"new"),(r2,"menu")]; return clicks

# main program

def main():
    pg.init()
    screen  = pg.display.set_mode((W,H), pg.RESIZABLE)
    pg.display.set_caption("Origin Pending") # title
    surf    = pg.Surface((W,H))
    clock   = pg.time.Clock()
    fonts   = make_fonts()
    room    = pg.transform.smoothscale(pg.image.load(os.path.join(ASSETS,"room.png")).convert(),(W,H))
    sb      = pg.transform.smoothscale(pg.image.load(os.path.join(ASSETS,"white.png")).convert_alpha(),(W,H))
    icon    = pg.transform.smoothscale(pg.image.load(os.path.join(ASSETS, "icon.png")).convert(), (W,H)) # game icon
    pg.display.set_icon(icon)
    def tint(rgb):
        s=sb.copy(); t=pg.Surface(s.get_size(),pg.SRCALPHA); t.fill((*rgb,255))
        s.blit(t,(0,0),special_flags=pg.BLEND_RGBA_MULT); return s

    session = {"right":0,"wrong":0,"streak":0} # no need to save this really long-term so
    scene   = "menu"; game=None; si=None; scale=1.0; offset=(0,0)

    def vmouse():
        mx,my=pg.mouse.get_pos(); ox,oy=offset
        return ((mx-ox)/scale,(my-oy)/scale)

    def go(action, val=None):
        nonlocal scene,game,si
        if action=="quit": pg.quit(); sys.exit()
        elif action=="new":
            game=new_game(); si=tint(game["case"]["suspect"]["rgb"]); scene="room"
        elif action=="menu":  scene="menu"
        elif action=="room":  game["notes_open"]=False; game["notes_typing"]=False; scene="room"
        elif action=="computer": game["notes_open"]=False; scene="computer"
        elif action=="verdict":  game["notes_open"]=False; scene="verdict"
        elif action=="ask":   ask(game,val)
        elif action=="db_tab":  game["tab"]=val; game["page"]=0
        elif action=="db_clear": game["query"]=""; game["page"]=0
        elif action=="review":
            ev=review(game,val)
            if ev: game["talk"]=f"You reviewed '{ev['label']}'. Ask the suspect about it."
        elif action=="toggle_notes": game["notes_open"]=not game["notes_open"]; game["notes_typing"]=False
        elif action=="notes_tab": game["notes_tab"]=val
        elif action=="focus_notes": game["notes_typing"]=True
        elif action=="log_page":
            per=10; mx=max(0,math.ceil(len(game["log"])/per)-1)
            game["log_page"]=max(0,min(mx,game.get("log_page",0)+val))
        elif action=="db_page": game["page"]=max(0,game["page"]+val)
        elif action=="pick":   game["picked"]=val
        elif action=="submit" and game["picked"]:
            game["verdict"]=game["picked"]
            if game["verdict"]==game["case"]["giver"]["name"]: session["right"]+=1; session["streak"]+=1
            else: session["wrong"]+=1; session["streak"]=0
            scene="result"

    while True:
        mouse = vmouse()
        if   scene=="menu":     clicks=draw_menu(surf,fonts,mouse,session)
        elif scene=="room":     clicks=draw_room(surf,fonts,game,mouse,room,si)
        elif scene=="computer": clicks=draw_database(surf,fonts,game,mouse)
        elif scene=="verdict":  clicks=draw_verdict(surf,fonts,game,mouse)
        elif scene=="result":   clicks=draw_result(surf,fonts,game,mouse,session)
        else: clicks=[]
        sw,sh=screen.get_size(); scale=min(sw/W,sh/H)
        dw,dh=int(W*scale),int(H*scale); ox,oy=(sw-dw)//2,(sh-dh)//2
        offset=(ox,oy); screen.fill(BLACK)
        screen.blit(pg.transform.smoothscale(surf,(dw,dh)),(ox,oy))
        pg.display.flip()
        for event in pg.event.get():
            if event.type==pg.QUIT: pg.quit(); sys.exit()
            if event.type==pg.VIDEORESIZE: screen=pg.display.set_mode((event.w,event.h),pg.RESIZABLE)
            if event.type==pg.KEYDOWN:
                if scene=="computer" and game and not game.get("notes_typing"):
                    if event.key==pg.K_BACKSPACE: game["query"]=game["query"][:-1]; game["page"]=0
                    elif event.key==pg.K_ESCAPE: go("room")
                    elif event.unicode and event.unicode.isprintable() and len(game["query"])<32:
                        game["query"]+=event.unicode; game["page"]=0
                elif game and game.get("notes_typing"):
                    if event.key==pg.K_BACKSPACE: game["notes"]=game["notes"][:-1]
                    elif event.key==pg.K_ESCAPE: game["notes_typing"]=False
                    elif event.key==pg.K_RETURN and len(game["notes"])<600: game["notes"]+="\n"
                    elif event.unicode and event.unicode.isprintable() and len(game["notes"])<600:
                        game["notes"]+=event.unicode
            if event.type==pg.MOUSEBUTTONDOWN and event.button==1:
                vx,vy=vmouse()
                if game and game.get("notes_typing"): game["notes_typing"]=False
                for item in reversed(clicks):
                    r,a,*v=item
                    if r.collidepoint((vx,vy)): go(a,v[0] if v else None); break
        clock.tick(FPS)

if __name__=="__main__": main() # i lowkey forgot what this is for, i just see it a lot
