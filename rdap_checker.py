import requests

# Attempted RDAP endpoints for certain TLDs
# NOTE: Some of these may or may not exist in reality.
# For official data, check IANA’s RDAP bootstrap registry:
# https://www.iana.org/assignments/rdap-bootstrap/rdap-bootstrap.xhtml
RDAP_SERVERS = {
    # .io (ccTLD for British Indian Ocean Territory)
    # Officially, it might not have a fully public RDAP. This is a guess.
    "io": "https://rdap.nic.io/domain/",

    # .ai (ccTLD for Anguilla)
    # Likely no official RDAP. This is a guess, may return 404.
    "ai": "https://rdap.nic.ai/domain/",

    # .app (gTLD owned by Google)
    # This *does* exist. If it stops working, check updated docs.
    "app": "https://rdap.nic.app/domain/",

    # .xyz (popular modern gTLD)
    # This should work:
    "xyz": "https://rdap.nic.xyz/domain/",

    # .dev (gTLD by Google)
    "dev": "https://rdap.nic.dev/domain/"
}

def check_domain_rdap(domain: str) -> bool:
    """
    Checks availability of 'domain' via the TLD's RDAP endpoint.

    Returns True if domain is AVAILABLE (i.e., not found in RDAP),
    Returns False if domain is TAKEN or if the TLD doesn't have a known working RDAP.
    """

    parts = domain.strip().split(".")
    if len(parts) < 2:
        raise ValueError(f"Invalid domain format: {domain}")

    # Extract TLD (last part)
    tld = parts[-1].lower()

    # Look up the RDAP base URL
    if tld not in RDAP_SERVERS:
        print(f"No known RDAP server for TLD: {tld}")
        return False  # Or raise an exception or revert to another method

    base_url = RDAP_SERVERS[tld]
    # Construct the full RDAP URL
    rdap_url = base_url + domain  # e.g. https://rdap.nic.io/domain/example.io

    try:
        response = requests.get(rdap_url, timeout=10)
        # RDAP convention: 404 = not found -> domain is likely AVAILABLE
        if response.status_code == 404:
            return True
        elif response.status_code == 200:
            # 200 = domain found in registry = TAKEN
            return False
        else:
            # Could be 403, 429 (rate limit), 503, etc.
            # We'll assume we can't confirm it's unregistered, so call it TAKEN (False).
            print(f"[WARN] Unexpected HTTP {response.status_code} for {domain}")
            return False

    except requests.exceptions.RequestException as e:
        # Network error, timeout, etc. 
        print(f"[ERROR] Request to {rdap_url} failed: {e}")
        return False

if __name__ == "__main__":
    # Test some domains on the TLDs we (hypothetically) support:
    test_domains = [
        "google.io",    # almost certainly taken
        "something.ai", # often taken, but let's see what RDAP says
        "randomstuff.ai",
        "mybrandnewdomain.io",
        "example.app",  # definitely taken
        "unusedxyz999.app",  # might or might not be available
        "coolproject.dev",
        "random999999.dev",
        "nonexistentexample123.xyz"
    ]

    print("=== RDAP Availability Checks ===")
    for d in test_domains:
        is_avail = check_domain_rdap(d)
        status_str = "AVAILABLE" if is_avail else "TAKEN"
        print(f"{d} → {status_str}")
