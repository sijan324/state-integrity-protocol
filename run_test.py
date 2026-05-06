from sip import StateIntegrityProtocol
sip = StateIntegrityProtocol(threshold=0.15)
sip.anchor("Summarize the quarterly report in three points.")
res1 = sip.observe("Here are the three points from the report...")
print(f"Test 1 - Drift: {res1.drift:.4f}, Aligned: {res1.is_aligned}")
res2 = sip.observe("The sky is blue and it might rain today.")
print(f"Test 2 - Drift: {res2.drift:.4f}, Aligned: {res2.is_aligned}")