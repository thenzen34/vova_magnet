from magnet_data_class import MagnetsData

data = MagnetsData()
file_name = '888.magnets34'
handle = open(file_name, 'rb')
data.load_system_from_stream(handle)
# списки смежности
graph = {}
for stick in data.sticks:
    start, end = sorted([stick.start_ball_id, stick.end_ball_id])
    if not graph.get(start, False):
        graph[start] = [end]
    else:
        graph[start].append(end)
    if not graph.get(end, False):
        graph[end] = [start]
    else:
        graph[end].append(start)
handle.close()

'''
for x in graph:
    graph[x].sort(reverse=True)
'''

# print(graph)

def find(items, cur, ix, end_ix, step=0, paths=None):
    if paths is None:
        paths = []
    i = 0
    while i < len(items[ix]):
        x = items[ix][i]
        if x == end_ix:
            if paths.count(cur) == 0:
                if len(cur) > 2:
                    paths.append(cur.copy())
        if x not in cur:
            cur.append(x)
            if step < 5:
                res = find(items, cur, x, end_ix, step + 1, paths)
                for y in res:
                    if paths.count(y) == 0:
                        if len(y) > 2:
                            paths.append(y.copy())
            cur.remove(x)

        i += 1
    return paths


r = find(graph, [0], 0, 0)
for y in r:
    print(y)
