#streamlit run rdap_streamlit.py


import streamlit as st
import requests
import string
import itertools
import pandas as pd

# Known RDAP endpoints for certain TLDs (may or may not actually work for .io/.ai)
RDAP_SERVERS = {
    "io": "https://rdap.nic.io/domain/",
    "ai": "https://rdap.nic.ai/domain/",
    "app": "https://rdap.nic.app/domain/",
    "xyz": "https://rdap.nic.xyz/domain/",
    "dev": "https://rdap.nic.dev/domain/"
}

def check_domain_rdap(domain: str) -> bool:
    """
    Checks availability of 'domain' via the TLD's RDAP endpoint.

    Returns True if domain is AVAILABLE (i.e., not found in RDAP => HTTP 404),
    Returns False if domain is TAKEN (HTTP 200) or if some other status is encountered.
    """
    parts = domain.strip().split(".")
    if len(parts) < 2:
        return False  # invalid domain

    tld = parts[-1].lower()

    if tld not in RDAP_SERVERS:
        # No known RDAP server for this TLD
        return False

    base_url = RDAP_SERVERS[tld]
    rdap_url = base_url + domain  # e.g., https://rdap.nic.io/domain/mydomain.io

    try:
        response = requests.get(rdap_url, timeout=10)
        if response.status_code == 404:
            # "Not found" typically means AVAILABLE
            return True
        elif response.status_code == 200:
            # 200 => Registered => TAKEN
            return False
        else:
            # Unexpected status code => assume TAKEN or uncertain
            return False
    except requests.exceptions.RequestException:
        # Network error or timeout => assume TAKEN or uncertain
        return False

def main():
    st.title("RDAP Domain Availability Checker")

    st.write(
        """
        This tool checks domain availability for certain modern TLDs using the RDAP protocol.
        **Note**: Some TLDs (like .io or .ai) might not have fully functional public RDAP servers,
        so results can be misleading. For truly reliable data, consider a registrar API or WHOIS fallback.
        """
    )

    # Sidebar controls
    tld_options = list(RDAP_SERVERS.keys())  # only TLDs we have in RDAP_SERVERS
    chosen_tld = st.sidebar.selectbox("Select TLD", tld_options, index=0)

    domain_length = st.sidebar.slider(
        "Number of characters:",
        min_value=1,
        max_value=3,
        value=2,
        help="Generate all alphabetical combinations of this length (a–z)."
    )

    if st.sidebar.button("Check Domains"):
        st.subheader(f"Checking all {domain_length}-char domains ending with .{chosen_tld}")

        # Generate domains
        letters = string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
        combos = itertools.product(letters, repeat=domain_length)  # e.g. aa, ab, ...
        possible_domains = ["".join(c) + "." + chosen_tld for c in combos]
        total_count = len(possible_domains)

        # Progress UI
        progress_bar = st.progress(0)
        status_info = st.empty()

        results_available = []
        for i, dom in enumerate(possible_domains):
            status_info.text(f"Currently checking: {dom}")
            is_avail = check_domain_rdap(dom)
            if is_avail:
                results_available.append(dom)
            progress_bar.progress(int((i+1)/total_count * 100))

        status_info.text("Done.")
        st.write(f"**Found {len(results_available)} available domains** (out of {total_count}).")

        if results_available:
            df = pd.DataFrame({"Available Domains": results_available})
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
