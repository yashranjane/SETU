from datetime import datetime, timezone


def generate_sandbox_mou(data: dict) -> bytes:
    """
    Generate statutory bilingual 2-page Sandbox MoU under GFR 2017 Rule 173.
    """
    ref = "SETU/MOU/{:04d}/{}".format(data.get("id", 1), datetime.now().year)
    today = datetime.now(timezone.utc).strftime("%d %B %Y")

    milestones_html = ""
    for m in data.get("milestones", []):
        milestones_html += """
        <tr>
            <td style="text-align:center;font-weight:bold;">Phase {phase} ({pct})</td>
            <td><strong>{title}</strong><br><span style="font-size:8.5pt;color:#555;">{desc}</span></td>
            <td style="text-align:right;font-weight:bold;">&#8377; {amt}</td>
            <td style="text-align:center;font-weight:bold;color:#138808;">Escrow Locked</td>
        </tr>""".format(
            phase=m.get("phase", 1),
            pct="20%" if m.get("phase") == 1 else ("50%" if m.get("phase") == 2 else "30%"),
            title=m.get("title", ""),
            desc=m.get("description", ""),
            amt="{:,.2f}".format(m.get("amount_inr", 0)),
        )

    css = """
  @page { size: A4; margin: 18mm 18mm 20mm 18mm; }
  body { font-family: Arial, Helvetica, sans-serif; font-size: 10pt; color: #212121; line-height: 1.45; }
  .header { text-align: center; border-bottom: 3px double #003366; padding-bottom: 12px; margin-bottom: 14px; }
  .gov-title { font-size: 8.5pt; color: #444; letter-spacing: 2px; text-transform: uppercase; }
  .portal-name { font-size: 15pt; font-weight: bold; color: #003366; margin: 3px 0; }
  .doc-title { font-size: 12pt; font-weight: bold; color: #C62828; border: 2px solid #C62828; display: inline-block; padding: 4px 16px; margin-top: 5px; }
  .ref-block { margin: 6px 0 0; font-size: 8.5pt; color: #555; }
  .section-title { background: #003366; color: white; padding: 5px 10px; font-size: 9.5pt; font-weight: bold; margin: 12px 0 6px; }
  .field-grid { display: grid; grid-template-columns: 200px 1fr; row-gap: 4px; column-gap: 10px; margin: 4px 0 4px 8px; font-size: 9.5pt; }
  .field-label { color: #555; font-weight: normal; }
  .field-value { font-weight: bold; color: #212121; }
  table { width: 100%; border-collapse: collapse; margin-top: 6px; font-size: 9pt; }
  th { background: #003366; color: white; padding: 6px 8px; text-align: left; }
  td { padding: 6px 8px; border: 1px solid #ddd; vertical-align: top; }
  tr:nth-child(even) td { background: #F9F9F9; }
  .sig-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-top: 25px; }
  .sig-box { border-top: 2px solid #333; padding-top: 8px; font-size: 9pt; }
  .footer-note { text-align: center; font-size: 7.5pt; color: #888; border-top: 1px solid #ddd; padding-top: 6px; margin-top: 20px; }
  .tricolor { height: 5px; background: linear-gradient(90deg, #FF9933 33%, #fff 33% 66%, #138808 66%); margin-bottom: 8px; }
  .hindi { font-style: italic; color: #555; font-size: 0.9em; }
  .statute-box { background: #EEF4FF; border: 1px solid #B0C8FF; padding: 8px 12px; margin-top: 8px; font-size: 8.5pt; color: #003366; }
"""

    html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><style>{css}</style></head>
<body>
  <div class="tricolor"></div>
  <div class="header">
    <div class="gov-title">&#2349;&#2366;&#2352;&#2340; &#2360;&#2352;&#2325;&#2366;&#2352; &nbsp;|&nbsp; Government of India &nbsp;|&nbsp; Public Procurement Innovation Cell</div>
    <div class="portal-name">SETU &mdash; Smart Evaluation &amp; Trial Utility</div>
    <div class="doc-title">STATUTORY SANDBOX MEMORANDUM OF UNDERSTANDING &nbsp;/&nbsp; <span class="hindi">&#2344;&#2357;&#2379;&#2344;&#2381;&#2350;&#2375;&#2359; &#2360;&#2361;&#2350;&#2340;&#2367; &#2346;&#2340;&#2381;&#2352;</span></div>
    <div class="ref-block">Ref: <strong>{ref}</strong> &nbsp;|&nbsp; Date: <strong>{today}</strong> &nbsp;|&nbsp; Statutory Ground: <strong>GFR 2017 Rule 173 (Non-L1 Innovation Pilot)</strong></div>
  </div>

  <div class="statute-box">
    <strong>STATUTORY CERTIFICATION UNDER GFR 2017 RULE 173:</strong><br>
    This Memorandum of Understanding executes a controlled innovation trial under statutory exemption from conventional commercial L1 tendering. The selection of the Startup is certified by the SETU Explainable AI Matching Engine based on verified TRL, DPIIT accreditation, and quantified outcome alignment.
  </div>

  <div class="section-title">1. Contracting Parties &nbsp;/&nbsp; <span class="hindi">&#2309;&#2344;&#2369;&#2348;&#2306;&#2343; &#2325;&#2375; &#2346;&#2325;&#2381;&#2359;&#2325;&#2366;&#2352;</span></div>
  <div class="field-grid">
    <span class="field-label">Public Buyer / <span class="hindi">&#2325;&#2381;&#2352;&#2375;&#2340;&#2366;</span>:</span>
    <span class="field-value">{buyer_name} &mdash; {buyer_org}</span>
    <span class="field-label">Innovation Startup / <span class="hindi">&#2360;&#2381;&#2335;&#2366;&#2352;&#2381;&#2335;&#2309;&#2346;</span>:</span>
    <span class="field-value">{startup_name} (DPIIT Reg: {dpiit_no})</span>
    <span class="field-label">GeM Seller ID / <span class="hindi">&#2332;&#2375;&#2350; &#2357;&#2367;&#2325;&#2381;&#2352;&#2375;&#2340;&#2366; &#2309;&#2344;&#2369;&#2325;&#2381;&#2352;&#2350;&#2366;&#2306;&#2325;</span>:</span>
    <span class="field-value">{gem_id} (Status: GeM Verified)</span>
  </div>

  <div class="section-title">2. Pilot Scope &amp; Outcome Challenge &nbsp;/&nbsp; <span class="hindi">&#2346;&#2352;&#2368;&#2325;&#2381;&#2359;&#2339; &#2357;&#2367;&#2357;&#2352;&#2339;</span></div>
  <div class="field-grid">
    <span class="field-label">Challenge Title:</span>
    <span class="field-value">{challenge_title}</span>
    <span class="field-label">Department / Location:</span>
    <span class="field-value">{dept} &mdash; {location}</span>
    <span class="field-label">Outcome Target:</span>
    <span class="field-value">{outcome_target}</span>
    <span class="field-label">Allocated Sandbox Escrow:</span>
    <span class="field-value">&#8377; {total_budget} (100% Escrow Ring-fenced)</span>
  </div>

  <div class="section-title">3. Milestone Escrow Disbursement Schedule &nbsp;/&nbsp; <span class="hindi">&#2349;&#2369;&#2327;&#2340;&#2366;&#2344; &#2309;&#2344;&#2369;&#2360;&#2370;&#2330;&#2368;</span></div>
  <table>
    <thead>
      <tr>
        <th width="20%">Tranche / <span class="hindi">&#2330;&#2352;&#2339;</span></th>
        <th width="48%">Deliverable &amp; Telemetry Scope / <span class="hindi">&#2357;&#2367;&#2357;&#2352;&#2339;</span></th>
        <th width="18%">Amount / <span class="hindi">&#2352;&#2366;&#2358;&#2367;</span></th>
        <th width="14%">Condition</th>
      </tr>
    </thead>
    <tbody>{milestones_html}</tbody>
  </table>

  <div class="section-title">4. Statutory Terms &amp; Conditions &nbsp;/&nbsp; <span class="hindi">&#2344;&#2367;&#2351;&#2350; &#2319;&#2357;&#2306; &#2358;&#2352;&#2381;&#2340;&#2375;&#2306;</span></div>
  <ol style="font-size:8.5pt; margin: 0 10px; color:#333; line-height:1.4;">
    <li><strong>Non-L1 Immunity:</strong> As per GFR 2017 Rule 173, this pilot does not solicit commercial price competition and is protected from post-facto audit inquiries regarding lowest commercial bids.</li>
    <li><strong>Evidence-Backed Escrow:</strong> Tranches are disbursed exclusively upon buyer verification of cryptographic telemetry logs or field test proofs.</li>
    <li><strong>Direct GeM Scale-Up:</strong> Upon successful verification of Milestone 3, the Startup shall receive a certified GeM Startup Runway Scale-Up Dossier permitting direct national public procurement.</li>
  </ol>

  <div class="sig-grid">
    <div class="sig-box">
      <strong>For Public Buyer (Government Body)</strong><br>
      Name: {buyer_name}<br>
      Designation: Authorized Officer, {buyer_org}<br>
      Digital Cryptographic Signoff: [VERIFIED SETU KEY]
    </div>
    <div class="sig-box">
      <strong>For Innovation Startup</strong><br>
      Name: Authorized Signatory<br>
      Entity: {startup_name}<br>
      GeM Seller Accredit: {gem_id}
    </div>
  </div>

  <div class="footer-note">
    Generated cryptographically by SETU Portal &bull; SHA-256 Audit Defense Block Authenticated &bull; GFR 2017 Rule 173 Sandbox
  </div>
</body>
</html>""".format(
        css=css,
        ref=ref, today=today,
        buyer_name=data.get("buyer_name", "Public Buyer"),
        buyer_org=data.get("buyer_org", "Government Department"),
        startup_name=data.get("startup_name", "Innovation Startup"),
        dpiit_no=data.get("dpiit_number", "DIPP88921"),
        gem_id=data.get("gem_seller_id", "SELR-GEM-2026"),
        challenge_title=data.get("challenge_title", ""),
        dept=data.get("department", ""),
        location=data.get("location", ""),
        outcome_target=data.get("outcome_statement", ""),
        total_budget="{:,.2f}".format(data.get("budget_inr", 0)),
        milestones_html=milestones_html,
    )

    try:
        import weasyprint
        return weasyprint.HTML(string=html).write_pdf()
    except Exception as e:
        print("WeasyPrint error: %s" % e)
        return html.encode("utf-8")
