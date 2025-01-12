#pip install networkx matplotlib
import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Add nodes and edges
edges = [
    ('A', 'B', 2),
    ('A', 'D', 1),
    ('B', 'C', 3),
    ('B', 'D', 7),
    ('C', 'D', 11)
]

G.add_weighted_edges_from(edges)

# Draw the graph
pos = nx.spring_layout(G)  # Layout for node positioning
plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightblue', font_size=12, font_weight='bold', edge_color='gray')

# Draw edge labels (weights)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Show the plot
plt.title("Graph: A, B, C, D")
plt.show()
