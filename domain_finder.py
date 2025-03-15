import streamlit as st
import whois
import string
import itertools
import pandas as pd
import time

def check_domain_whois(domain):
    """
    Attempt a WHOIS lookup. If the raw text includes typical 
    'no match' or 'not found' strings, we consider it available.
    If 'domain_name' is parsed, we consider it taken.

    NOTE: This is a heuristic. Different TLDs sometimes
    require special handling. Consider a registrar API for accuracy.
    """
    try:
        w = whois.whois(domain)
        raw_text = (w.text or "").lower()

        # Look for "not found" patterns in the raw WHOIS text:
        if "no match" in raw_text or "not found" in raw_text or "no data found" in raw_text:
            return True  # "Likely available"

        # If python-whois doesn't parse domain_name, treat it as available:
        if not w.domain_name:
            return True

        # Otherwise, assume it's taken
        return False
    except Exception:
        # If there's an error (e.g. rate limit, server error), assume taken or uncertain
        return False

def main():
    st.title("Short Domain Availability Checker")

    st.write(
        """
        **Instructions**  
        1. Enter a TLD (e.g., "com" or "net") in the sidebar.  
        2. Specify how many characters the domain should have (e.g., 2).  
        3. Click "Check Domains" to generate & check them.  
        
        The tool will:
        - Generate *all* possible domains of that length (using letters a–z).  
        - Show a progress bar as it checks each domain.  
        - Display *only* those domains it believes are available, in a 
          2-column table with a clickable link and a verified status.
        """
    )

    # Sidebar: TLD and domain length
    tld = st.sidebar.text_input("Enter TLD (no leading dot)", value="com")
    domain_length = st.sidebar.number_input(
        "Number of characters:",
        min_value=1,
        max_value=10,
        value=2
    )

    # "Check Domains" button
    if st.sidebar.button("Check Domains"):
        st.subheader(f"Checking all {domain_length}-char domains ending with .{tld}")

        # Generate all combos of given length (letters only)
        chars = string.ascii_lowercase
        possible_domains = [
            "".join(c) for c in itertools.product(chars, repeat=domain_length)
        ]
        total_count = len(possible_domains)

        # Progress bar + status display
        progress_bar = st.progress(0)
        status_text = st.empty()

        results = []
        for i, name in enumerate(possible_domains):
            full_domain = f"{name}.{tld}"
            
            # Update status
            status_text.info(f"Currently checking: **{full_domain}**")

            # WHOIS check
            available = check_domain_whois(full_domain)
            results.append({
                "Domain": full_domain,
                "Available": available
            })

            # Update progress bar
            progress_value = (i + 1) / total_count
            progress_bar.progress(progress_value)

            # Optional small pause to avoid rate-limiting
            # time.sleep(0.2)

        # Filter for available domains only
        df = pd.DataFrame(results)
        df_available = df[df["Available"] == True].copy()

        # Create a link column (markdown format). Use https:// to ensure clickable
        df_available["Domain"] = df_available["Domain"].apply(
            lambda d: f"[{d}](https://{d})"
        )
        # Create a "Status" column with green text + checkmark
        df_available["Status"] = "✅ **:green[Verified]**"

        # Drop the "Available" column, we only want the Domain and Status
        df_available = df_available[["Domain", "Status"]]

        # Display the final table as HTML to preserve clickable links
        st.write("### Available Domains:")
        if df_available.empty:
            st.write("No available domains found.")
        else:
            st.markdown(df_available.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Final note
        st.write("""
        **Disclaimer**: This WHOIS-based check can be inaccurate.  
        For more reliable data, use a domain registrar API 
        (e.g., GoDaddy, Namecheap).
        """)

if __name__ == "__main__":
    main()
