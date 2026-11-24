"""Build the illustrative mock-up pages (HTML) used for the README images.

The screens follow the real application's layout, fields and workflow, filled with
invented content. They are illustrations, not screenshots of the running product.
Run:  python mockups/build.py   then capture each page at 1440 x 900.
"""
from pathlib import Path

HERE = Path(__file__).parent


def side(active: str) -> str:
    items = [("Dashboard", "dash"), ("Lessons", "lessons"), ("New lesson", "new"),
             ("My approvals", "review"), ("Search & suggestions", "search"),
             ("Best practices", "bp"), ("Import", "import")]
    admin = [("Programmes", ""), ("Review policies", ""), ("Partners", ""),
             ("Integrations", ""), ("Billing", "")]
    nav = "".join(
        f'<a class="{"on" if k == active else ""}">{n}'
        + ('<span class="badge">3</span>' if k == "review" else "") + "</a>" for n, k in items)
    adm = "".join(f"<a>{n}</a>" for n, _ in admin)
    return (f'<aside class="side"><div class="brand"><div class="logo">E</div>EnzaTrack</div>'
            f'<div class="org">Demo Health Programme</div><nav class="nav">{nav}'
            f'<div class="sec">Organisation</div>{adm}</nav></aside>')


def page(title: str, active: str, body: str) -> str:
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="style.css"></head><body><div class="app">{side(active)}
<main class="main"><div class="top"><h1>{title}</h1><div class="search">Search lessons, programmes,
countries...</div><span class="lang">EN · FR · PT · ES · SW</span><div class="avatar">AN</div></div>
{body}</main></div><div class="mock">Illustrative mock-up · invented content</div></body></html>"""


def bars(rows):
    top = max(v for _, v in rows)
    return "".join(f'<div class="row" style="margin:7px 0"><span style="width:150px">{n}</span>'
                   f'<div class="track"><div class="bar" style="width:{v / top * 100:.0f}%"></div>'
                   f'</div><b style="width:34px;text-align:right">{v}</b></div>' for n, v in rows)


DASH = page("Dashboard", "dash", f"""
<div class="grid" style="grid-template-columns:repeat(4,1fr)">
 <div class="card k"><b>248</b><span>approved lessons</span><br><small>+19 this quarter</small></div>
 <div class="card k"><b>14</b><span>under review</span><br><small class="muted">3 waiting for you</small></div>
 <div class="card k"><b>63</b><span>contributors</span><br><small>+8 this quarter</small></div>
 <div class="card k"><b>11</b><span>best practices</span><br><small>2 new candidates</small></div>
</div>
<div class="grid" style="grid-template-columns:1.15fr 1fr;margin-top:16px">
 <div class="card"><h2>Approved lessons by domain</h2>{bars([("Immunization", 71), ("Malaria", 52),
  ("Supply chain", 38), ("Data & information", 33), ("Community engagement", 29),
  ("Emergency response", 25)])}</div>
 <div class="card"><h2>Suggested for you</h2>
  <table><tr><th>Lesson</th><th>Why</th></tr>
  <tr><td>Microplanning with community health workers raised outreach coverage</td>
   <td><span class="pill p-ind">your programme + country</span></td></tr>
  <tr><td>Cold-chain temperature alerts by SMS cut vaccine losses</td>
   <td><span class="pill p-blu">similar to lessons you read</span></td></tr>
  <tr><td>Weekly district data review meetings improved reporting completeness</td>
   <td><span class="pill p-grn">trending in your domain</span></td></tr>
  <tr><td>Pre-positioning test kits before the rainy season</td>
   <td><span class="pill p-gry">new this week</span></td></tr></table></div>
</div>
<div class="grid" style="grid-template-columns:1.15fr 1fr;margin-top:16px">
 <div class="card"><h2>Recently approved</h2><table>
  <tr><th>Title</th><th>Programme</th><th>Countries</th><th>Rating</th><th>Visibility</th></tr>
  <tr><td>Integrating HPV vaccination into school health days</td><td>Immunization</td><td>3</td><td>4.6</td><td><span class="pill p-grn">Public</span></td></tr>
  <tr><td>Digital stock cards reduced stock-outs at health facilities</td><td>Supply chain</td><td>2</td><td>4.3</td><td><span class="pill p-blu">Partners</span></td></tr>
  <tr><td>Rapid response teams: what made deployment faster</td><td>Emergencies</td><td>4</td><td>4.1</td><td><span class="pill p-gry">Org only</span></td></tr>
  <tr><td>Engaging religious leaders to address vaccine hesitancy</td><td>Immunization</td><td>2</td><td>4.5</td><td><span class="pill p-grn">Public</span></td></tr>
 </table></div>
 <div class="card"><h2>Top contributors this quarter</h2><table>
  <tr><th>Contributor</th><th>Lessons</th><th>Reviews</th></tr>
  <tr><td>A. Niyonzima</td><td>7</td><td>12</td></tr><tr><td>M. Ochieng</td><td>6</td><td>9</td></tr>
  <tr><td>F. Diallo</td><td>5</td><td>11</td></tr><tr><td>J. Mutasa</td><td>4</td><td>6</td></tr></table></div>
</div>""")


def steps(cur):
    names = ["Context", "Actions", "Outcomes", "Lesson", "Evidence & risks", "Sharing & review"]
    out = []
    for i, n in enumerate(names, 1):
        st = "done" if i < cur else "cur" if i == cur else ""
        col = {"done": "#16a34a", "cur": "#4f46e5"}.get(st, "#c3c8d4")
        out.append(f'<div class="row" style="flex:1"><span style="width:26px;height:26px;border-radius:50%;'
                   f'background:{col};color:#fff;display:grid;place-items:center;font-weight:700;font-size:12px">'
                   f'{"✓" if st == "done" else i}</span><span style="font-weight:{700 if st == "cur" else 500}">{n}</span></div>')
    return '<div class="card row" style="gap:6px;margin-bottom:16px">' + "".join(out) + "</div>"


WIZARD = page("New lesson", "new", f"""{steps(4)}
<div class="grid" style="grid-template-columns:1.5fr 1fr">
 <div class="card"><h2>Step 4 of 6 · The lesson</h2>
  <div class="field"><label>Title</label><div class="input">Microplanning with community health workers raised outreach coverage</div></div>
  <div class="field"><label>Key lesson</label><div class="input ta">Outreach sessions planned together with community health workers, using their household lists, reached more zero-dose children than sessions planned at district level alone.</div></div>
  <div class="field"><label>Recommendations</label><div class="input ta">Involve community health workers in quarterly microplanning; share the session calendar with village leaders two weeks ahead; track zero-dose children by village.</div></div>
  <div class="grid" style="grid-template-columns:1fr 1fr">
   <div class="field"><label>Pre-conditions</label><div class="input">Active CHW network; updated household lists</div></div>
   <div class="field"><label>What to avoid</label><div class="input">Planning without the health facility in-charge</div></div></div>
  <div class="grid" style="grid-template-columns:1fr 1fr 1fr">
   <div class="field"><label>Programme</label><div class="input">Immunization</div></div>
   <div class="field"><label>Domains</label><div class="input"><span class="pill p-ind">Service delivery</span> <span class="pill p-ind">Community</span></div></div>
   <div class="field"><label>Countries</label><div class="input"><span class="pill p-gry">Country A</span> <span class="pill p-gry">Country B</span></div></div></div>
  <div class="row" style="margin-top:16px"><span class="muted">Draft saved automatically · 10:42</span>
   <span style="margin-left:auto"></span><span class="btn">Back</span><span class="btn pri">Next: evidence &amp; risks</span></div>
 </div>
 <div class="grid" style="align-content:start">
  <div class="card"><h2>Similar lessons already in the library</h2>
   <p class="muted" style="margin-top:-6px">Checked as you type, to avoid duplicates</p>
   <table><tr><td>Village-level session planning in hard-to-reach districts</td><td><span class="pill p-amb">86% similar</span></td></tr>
   <tr><td>Using CHW household registers to find zero-dose children</td><td><span class="pill p-amb">81%</span></td></tr>
   <tr><td>Fixed-post vs outreach: cost per child vaccinated</td><td><span class="pill p-gry">64%</span></td></tr></table>
   <div class="row" style="margin-top:10px"><span class="btn">Link as related</span><span class="btn">Add me as co-author</span></div></div>
  <div class="card"><h2>Contributors</h2><table><tr><td>A. Niyonzima</td><td><span class="pill p-ind">Author</span></td></tr>
   <tr><td>M. Ochieng</td><td><span class="pill p-gry">Co-author</span></td></tr></table></div>
  <div class="card"><h2>Start from a document</h2><p class="muted" style="margin:0">Upload a report (.docx, .pdf, .pptx), a ZIP folder or a SharePoint folder: the text is extracted and the fields pre-filled.</p></div>
 </div>
</div>""")


def rubric():
    dims = [("Impact", 0.25, 5), ("Applicability", 0.20, 4), ("Scalability", 0.20, 4),
            ("Usability", 0.15, 5), ("Evidence", 0.15, 3), ("Resources needed", 0.05, 4)]
    rows = "".join(f'<tr><td>{n}</td><td class="muted">{w:.0%}</td><td>'
                   + "".join(f'<span style="display:inline-block;width:22px;height:22px;border-radius:5px;margin-right:3px;'
                             f'background:{"#4f46e5" if i <= s else "#e5e7ef"}"></span>' for i in range(1, 6))
                   + f"</td><td><b>{s}</b></td></tr>" for n, w, s in dims)
    score = sum(w * s for _, w, s in dims)
    return rows, score


RUB, SCORE = rubric()
REVIEW = page("Review: round 2", "review", f"""
<div class="grid" style="grid-template-columns:1.35fr 1fr">
 <div class="card"><div class="row"><span class="pill p-amb">Under review</span><span class="pill p-gry">Round 2</span>
  <span class="muted">Due in 3 days · policy: Immunization programme</span></div>
  <h2 style="font-size:19px;margin:12px 0 6px">Microplanning with community health workers raised outreach coverage</h2>
  <p class="muted" style="margin:0 0 12px">A. Niyonzima, M. Ochieng · Immunization · Country A, Country B</p>
  <h2>Context</h2><p style="margin-top:-4px">Several districts had low outreach attendance and a growing number of zero-dose children despite a full session calendar.</p>
  <h2>Actions</h2><p style="margin-top:-4px">Community health workers joined quarterly microplanning, brought household lists, and announced sessions through village leaders.</p>
  <h2>Outcomes</h2><p style="margin-top:-4px">More zero-dose children reached in the pilot districts over two quarters; fewer cancelled sessions.</p>
  <h2>Changes since round 1</h2><p style="margin-top:-4px"><span class="pill p-grn">+ evidence link added</span> <span class="pill p-grn">+ cost section completed</span></p>
 </div>
 <div class="grid" style="align-content:start">
  <div class="card"><h2>Your rating</h2><table>{RUB}</table>
   <div class="row" style="margin-top:10px"><span class="muted">Weighted score</span><b style="margin-left:auto;font-size:20px">{SCORE:.2f} / 5</b></div></div>
  <div class="card"><h2>Decision</h2><div class="input ta">Clear and well evidenced. Please name the data source for the outcome figures before publishing.</div>
   <div class="row" style="margin-top:12px"><span class="btn ok">Approve</span><span class="btn warn">Request changes</span><span class="btn bad">Reject</span></div>
   <p class="hint">Approving makes the lesson visible according to its sharing level: Org only · Partners · Public.</p></div>
  <div class="card"><h2>Other reviewers</h2><table><tr><td>F. Diallo</td><td><span class="pill p-grn">Approved</span></td></tr>
   <tr><td>J. Mutasa</td><td><span class="pill p-gry">Pending</span></td></tr></table></div>
 </div>
</div>""")


def result(title, why, cls, meta, score):
    return (f'<div class="card" style="margin-bottom:12px"><div class="row"><b style="font-size:15px">{title}</b>'
            f'<span class="pill p-amb" style="margin-left:auto">{score}</span></div><p class="muted" style="margin:6px 0">{meta}</p>'
            f'<span class="pill {cls}">{why}</span></div>')


SEARCH = page("Search & suggestions", "search", f"""
<div class="card row" style="margin-bottom:16px"><div class="input" style="flex:1">how to reach zero-dose children in remote areas</div>
 <span class="btn pri">Search</span><span class="pill p-ind">Meaning-based search</span></div>
<div class="grid" style="grid-template-columns:240px 1fr 300px">
 <div class="card"><h2>Filters</h2>
  <div class="field"><label>Programme</label><div class="input">All</div></div>
  <div class="field"><label>Domain</label><div class="input">Service delivery</div></div>
  <div class="field"><label>Region / country</label><div class="input">East & Southern Africa</div></div>
  <div class="field"><label>Language</label><div class="input">Any (auto-translated)</div></div>
  <div class="field"><label>Sharing</label><div class="input">Mine + partners + public</div></div>
  <div class="field"><label>Minimum rating</label><div class="input">3.5</div></div></div>
 <div>
  {result("Using CHW household registers to find zero-dose children", "Close in meaning to your question", "p-ind", "Immunization · Country C · 2025 · rated 4.4 · Partners", "0.83")}
  {result("Mobile teams for nomadic communities: timing sessions with seasonal movement", "Close in meaning to your question", "p-ind", "Immunization · Country D · 2024 · rated 4.2 · Public · translated from French", "0.79")}
  {result("Village-level session planning in hard-to-reach districts", "Same domain + programme + country as you", "p-blu", "Immunization · Country A · 2025 · rated 4.0 · Org only", "0.77")}
  {result("Boat outreach on lake islands: what worked and what to avoid", "Similar to lessons you viewed", "p-grn", "Immunization · Country B · 2023 · rated 3.9 · Public", "0.71")}
 </div>
 <div class="grid" style="align-content:start">
  <div class="card"><h2>Best practice</h2><b>Plan outreach with the community, not for it</b>
   <p class="muted">Promoted from 4 approved lessons in 3 countries · average rating 4.3</p><span class="pill p-grn">Best practice</span></div>
  <div class="card"><h2>Compile</h2><p class="muted" style="margin-top:-4px">Add results to the basket to compare them side by side or generate a briefing paper (PDF or Word).</p>
   <div class="row"><span class="btn">Compare (2)</span><span class="btn pri">Generate paper</span></div></div>
 </div>
</div>""")

for name, html in [("dashboard", DASH), ("lesson_wizard", WIZARD), ("review", REVIEW),
                   ("search", SEARCH)]:
    (HERE / f"{name}.html").write_text(html, encoding="utf-8")
print("Mock-up pages written to", HERE)
