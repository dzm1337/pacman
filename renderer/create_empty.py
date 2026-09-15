def create_empty(w, h):
    empty = [[8] + [0] * (w - 2) + [2] for _ in range(h - 2)]
    empty.insert(0, [9] + [1] * (h - 2) + [3])
    empty.append([12] + [4] * (w - 2) + [6])
    return empty


maze = create_empty(6, 5)
for row in maze:
    print(row)
