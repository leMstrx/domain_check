import whois

domain = "ai.ai"
w = whois.whois(domain)

print("Parsed domain_name:", w.domain_name)
print("Raw text:\n", w.text)
