a = {
    "a": 5,
    "b": 3,
    "u": 4
}

t = []
for i in a.items():
    t.append(i)

t.sort(key=lambda k: k[1])
print(t)