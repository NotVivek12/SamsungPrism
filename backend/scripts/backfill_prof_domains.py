"""
Backfill prof_domain links so research areas appear in the UI.

Sources:
- Primary: Excel (prof.xlsx) column 'domain_expertise' (or similar aliases)
- Optional: Google Scholar interests (--use-google)

Behavior:
- Idempotent: checks for existing domains and mappings before inserting
- Prints BEFORE/AFTER counts for verification
"""

from __future__ import annotations

import argparse
import logging
import os
from typing import Dict, List, Optional, Tuple, Union

try:
    import pandas as pd  # type: ignore
    HAS_PANDAS = True
except Exception:
    HAS_PANDAS = False

# Reuse DB connection and env from the app
from database import get_connection, close_connection

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("backfill_prof_domains")


def find_excel_file(paths: List[str]) -> Optional[str]:
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


def normalize_domain(s: str) -> str:
    s = " ".join(str(s or "").strip().split())
    if not s:
        return s
    acronyms = {"nlp", "ai", "ml", "cv", "iot", "vlsi", "rfid", "hci"}
    lw = s.lower()
    if lw in acronyms:
        return lw.upper()
    return " ".join(w.upper() if w.lower() in acronyms else w.capitalize() for w in s.split())


def load_excel_domains(excel_path: str) -> Dict[str, List[str]]:
    """Return mapping from professor identity -> domain list.
    Keys used:
      - email:<email>
      - namecollege:<name>|<college>
    """
    if not HAS_PANDAS:
        raise RuntimeError("pandas is required to parse Excel; install via: python -m pip install pandas openpyxl")

    df = pd.read_excel(excel_path)
    cols = {c: str(c).strip().lower().replace(" ", "_") for c in df.columns}
    df = df.rename(columns=cols)

    name_col = next((c for c in ["name", "professor_name", "pname"] if c in df.columns), None)
    college_col = next((c for c in ["college", "institution", "cname"] if c in df.columns), None)
    email_col = next((c for c in ["email", "cmailid"] if c in df.columns), None)
    dom_col = next((c for c in [
        "domain_expertise", "domain", "domains", "domainname", "research_interests",
        "domain_expertise_1", "domain_expertise_2", "research areas", "research_areas"
    ] if c in df.columns), None)

    if not dom_col:
        logger.warning(
            "Excel: domain column not found. Available columns: %s",
            ", ".join(df.columns.astype(str).tolist())
        )
        return {}

    def norm(s: str) -> str:
        return " ".join(str(s or "").strip().lower().split())

    mapping: Dict[str, List[str]] = {}
    for _, row in df.iterrows():
        raw = str(row.get(dom_col, "")).strip()
        if not raw or raw.lower() == "nan":
            continue
        parts = [p.strip() for p in raw.replace("|", ",").split(",") if p and str(p).strip().lower() != "nan"]
        domains = [normalize_domain(p) for p in parts if p]
        if not domains:
            continue

        email = norm(row.get(email_col, "")) if email_col else ""
        if email:
            mapping[f"email:{email}"] = domains
            continue

        name = norm(row.get(name_col, "")) if name_col else ""
        college = norm(row.get(college_col, "")) if college_col else ""
        if name and college:
            mapping[f"namecollege:{name}|{college}"] = domains
        elif name:
            mapping[f"namecollege:{name}|"] = domains

    logger.info(f"Loaded {len(mapping)} professor keys from Excel")
    return mapping


def load_csv_domains(csv_path: str) -> Dict[int, List[str]]:
    """Load mapping from a CSV file. Supported headers:
    - ProfID, Domain (single domain per row)
    - ProfID, Domains (comma-separated)
    - PID, DomainName
    """
    mapping: Dict[int, List[str]] = {}
    try:
        if HAS_PANDAS and csv_path.lower().endswith((".csv", ".tsv")):
            sep = "," if csv_path.lower().endswith(".csv") else "\t"
            df = pd.read_csv(csv_path, sep=sep)
            cols = {c: str(c).strip().lower() for c in df.columns}
            df = df.rename(columns=cols)
            pid_col = next((c for c in ["profid", "pid", "id"] if c in df.columns), None)
            dom_single = next((c for c in ["domain", "domainname"] if c in df.columns), None)
            dom_multi = next((c for c in ["domains", "domain_list"] if c in df.columns), None)
            if not pid_col or not (dom_single or dom_multi):
                logger.warning("CSV: required headers not found (need ProfID and Domain(s))")
                return {}
            for _, row in df.iterrows():
                try:
                    pid = int(row.get(pid_col))
                except Exception:
                    continue
                raw = str(row.get(dom_single) if dom_single else row.get(dom_multi, "")).strip()
                if not raw or raw.lower() == "nan":
                    continue
                parts = [p.strip() for p in raw.replace("|", ",").split(",") if p.strip()]
                domains = [normalize_domain(p) for p in parts]
                if not domains:
                    continue
                mapping[pid] = domains
        else:
            import csv  # fallback
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                headers = {h.lower(): h for h in reader.fieldnames or []}
                pid_h = headers.get("profid") or headers.get("pid") or headers.get("id")
                dom_h = headers.get("domain") or headers.get("domainname") or headers.get("domains")
                if not pid_h or not dom_h:
                    logger.warning("CSV: required headers not found (need ProfID and Domain(s))")
                    return {}
                for row in reader:
                    try:
                        pid = int(row.get(pid_h, "").strip())
                    except Exception:
                        continue
                    raw = (row.get(dom_h, "") or "").strip()
                    if not raw:
                        continue
                    parts = [p.strip() for p in raw.replace("|", ",").split(",") if p.strip()]
                    domains = [normalize_domain(p) for p in parts]
                    if domains:
                        mapping[pid] = domains
    except Exception as e:
        logger.warning(f"CSV load failed: {e}")
        return {}
    logger.info(f"Loaded {len(mapping)} professor IDs from CSV")
    return mapping


def get_missing_professors(cursor) -> List[Dict]:
    cursor.execute(
        """
        SELECT p.PID as id, p.PName as name, p.CName as college, p.CMailId as email, pl.GScholar as gscholar
        FROM professors p
        LEFT JOIN prof_domain pd ON p.PID = pd.ProfID
        LEFT JOIN plink pl ON pl.ProfID = p.PID
        WHERE pd.ProfID IS NULL
        """
    )
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in cursor.fetchall()]


def get_all_professors_with_gs(cursor) -> List[Dict]:
    cursor.execute(
        """
        SELECT p.PID as id, p.PName as name, p.CName as college, p.CMailId as email, pl.GScholar as gscholar
        FROM professors p
        LEFT JOIN plink pl ON pl.ProfID = p.PID
        WHERE pl.GScholar IS NOT NULL AND pl.GScholar <> ''
        """
    )
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r)) for r in cursor.fetchall()]


def ensure_domain(cursor, name: str) -> int:
    cursor.execute("SELECT DomainID FROM domains WHERE LOWER(DomainName)=LOWER(%s) LIMIT 1", (name,))
    row = cursor.fetchone()
    if row:
        return int(row[0])
    cursor.execute("INSERT INTO domains (DomainName) VALUES (%s)", (name,))
    return int(cursor.lastrowid)


def ensure_prof_domain(cursor, prof_id: int, domain_id: int) -> bool:
    cursor.execute("SELECT 1 FROM prof_domain WHERE ProfID=%s AND DomainId=%s LIMIT 1", (prof_id, domain_id))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO prof_domain (ProfID, DomainId) VALUES (%s, %s)", (prof_id, domain_id))
    return True


def count_without_domains(cursor) -> int:
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM professors p
        LEFT JOIN prof_domain pd ON p.PID = pd.ProfID
        WHERE pd.ProfID IS NULL
        """
    )
    return int(cursor.fetchone()[0])


def backfill_from_excel(cursor, excel_map: Dict[str, List[str]], missing: List[Dict]) -> Tuple[int, int]:
    created_domains, created_links = 0, 0

    def norm(s: str) -> str:
        return " ".join(str(s or "").strip().lower().split())

    for prof in missing:
        email_key = f"email:{norm(prof.get('email'))}"
        name_key = f"namecollege:{norm(prof.get('name'))}|{norm(prof.get('college'))}"
        fallback_name_key = f"namecollege:{norm(prof.get('name'))}|"

        domains = excel_map.get(email_key) or excel_map.get(name_key) or excel_map.get(fallback_name_key)
        if not domains:
            continue

        for d in domains:
            dom_id = ensure_domain(cursor, d)
            if ensure_prof_domain(cursor, prof['id'], dom_id):
                created_links += 1
                # Count new domain rows best-effort (cannot easily know if newly created vs existing across tx)
                # This is fine for summary purposes
    return 0, created_links


def backfill_from_id_map(cursor, id_map: Dict[int, List[str]], missing: List[Dict]) -> int:
    missing_ids = {m["id"] for m in missing}
    created_links = 0
    for pid, domains in id_map.items():
        if pid not in missing_ids:
            continue
        for d in domains:
            dom_id = ensure_domain(cursor, d)
            if ensure_prof_domain(cursor, pid, dom_id):
                created_links += 1
    return created_links


def canonicalize_gs_url(url: str) -> str:
    """Return a valid Google Scholar profile URL if possible, else empty string.
    - Accepts full URLs.
    - If given a bare user id like 'ZpRkbnoAAAAJ', builds the standard URL.
    - Rejects non-Google-Scholar links.
    """
    u = (url or "").strip()
    if not u:
        return ""
    if u.lower().startswith("http"):
        # Only accept scholar.google.*
        if "scholar.google" in u.lower():
            return u
        return ""
    # Try to treat as user id token
    import re
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", u):
        return f"https://scholar.google.com/citations?hl=en&user={u}"
    return ""


def maybe_backfill_from_google(cursor, profs: List[Dict]) -> Tuple[int, int]:
    try:
        from google_scholar_extractor import extract_google_scholar_data  # lazy import
    except Exception:
        logger.warning("Google Scholar extractor not available; skipping GS enrichment")
        return (0, 0)

    created_domains, created_links = 0, 0
    for prof in profs:
        url = canonicalize_gs_url(prof.get("gscholar") or "")
        if not url:  # skip invalid or non-scholar
            continue
        try:
            data = extract_google_scholar_data(url) or {}
            interests = data.get("Google Scholar Data", {}).get("Research Interests", []) or []
        except Exception:
            continue

        for raw in interests[:5]:
            dname = normalize_domain(raw)
            dom_id = ensure_domain(cursor, dname)
            if ensure_prof_domain(cursor, prof['id'], dom_id):
                created_links += 1
    return created_domains, created_links


def main():
    parser = argparse.ArgumentParser(description="Populate prof_domain using DB (plink.GScholar) and optional CSV/Excel mappings")
    parser.add_argument("--csv", dest="csv_path", default=None, help="CSV mapping (ProfID, Domain or Domains)")
    parser.add_argument("--excel", dest="excel_path", default=None, help="Path to prof.xlsx (default: project root)")
    parser.add_argument("--use-google", action="store_true", help="If Excel lacks domains, enrich from Google Scholar interests")
    parser.add_argument("--db-only", action="store_true", help="Ignore Excel/CSV; only use DB + Google Scholar for enrichment")
    parser.add_argument("--enrich-all", action="store_true", help="Use Google Scholar interests for all professors with GS links (not just missing)")
    parser.add_argument("--dry-run", action="store_true", help="Do not commit DB changes")
    args = parser.parse_args()

    excel_path = args.excel_path or find_excel_file([
        os.path.join(os.getcwd(), "prof.xlsx"),
        os.path.join(os.path.dirname(os.getcwd()), "prof.xlsx"),
        os.path.join(os.path.dirname(__file__), "prof.xlsx"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "prof.xlsx"),
    ])

    # Load optional CSV/Excel mapping unless db-only
    csv_map: Dict[int, List[str]] = {}
    excel_map: Dict[str, List[str]] = {}
    if not args.db_only:
        if args.csv_path and os.path.exists(args.csv_path):
            logger.info(f"Reading CSV: {args.csv_path}")
            csv_map = load_csv_domains(args.csv_path)
        if excel_path and os.path.exists(excel_path):
            logger.info(f"Reading Excel: {excel_path}")
            excel_map = load_excel_domains(excel_path)
        else:
            if args.excel_path:
                logger.warning("Excel file not found; proceeding without Excel mapping")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        before_missing = count_without_domains(cur)
        logger.info(f"Professors without domains BEFORE: {before_missing}")

        missing = get_missing_professors(cur)
        # Prefer CSV mapping (explicit ProfID control), then Excel
        if csv_map:
            links_csv = backfill_from_id_map(cur, csv_map, missing)
            logger.info(f"CSV backfill links created: {links_csv}")
            missing = get_missing_professors(cur)
        if excel_map and missing:
            _, links1 = backfill_from_excel(cur, excel_map, missing)
            logger.info(f"Excel backfill links created: {links1}")

        links2 = 0
        if args.use_google:
            profs_target = get_all_professors_with_gs(cur) if args.enrich_all else get_missing_professors(cur)
            if profs_target:
                _, links2 = maybe_backfill_from_google(cur, profs_target)
                logger.info(f"Google Scholar backfill links created: {links2}")

        if args.dry_run:
            logger.info("Dry-run mode: rolling back changes")
            conn.rollback()
        else:
            conn.commit()

        after_missing = count_without_domains(cur)
        logger.info(f"Professors without domains AFTER: {after_missing}")

    finally:
        close_connection(conn, cur)


if __name__ == "__main__":
    main()

