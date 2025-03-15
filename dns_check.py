#Simple domain checking tool - to get the shortest domains available
import dns.resolver
import dns.exception
import string
import itertools

chars = string.ascii_lowercase # 'abcdefghijklmnopqrstuvwxyz'
# Generate all possible combinations of 1-2 characters
domain_names = []
#Generate 1-2 characters domain names
for i in range(1, 3):
    for comb in itertools.product(chars, repeat=i):
        domain_names.append(''.join(comb))
#All possibilities generated

def is_domain_available(domain):
    """
    Check domain by attempting to resolve DNS A record.
    If we get NXDOMAIN, likely it's not registered.
    This is not guaranteed for all TLDs, but a quick check.
    """
    try:
        answers = dns.resolver.resolve(domain, 'A')
        # If it resolves successfully, it's likely registered:
        return False
    except dns.exception.DNSException:
        # In case of NXDOMAIN or any error, we assume it's not resolved
        return True

# Now let's test some short domains:
tlds = ["io", "com", "ai", "de", "me", "app"]  # etc.
for d in domain_names:  # e.g., 'a', 'b', 'aa', 'ab' ...
    for t in tlds:
        full_domain = f"{d}.{t}"
        if is_domain_available(full_domain):
            print(f"Potentially available: {full_domain}")
