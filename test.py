import time
a = ["token","config","self.run","vars","help"]
b = "DISCORD_TOKEN"
print("token" in "DISCORD_TOKEN".lower())
illegal = ["token","config","self.run","vars","help"]
print(bool(set(illegal).intersection(b.lower())))
t0 = time.perf_counter()
for x in range(1):
    print(bool(set(a) & set(b)))
t1 = time.perf_counter()
print(t1-t0)