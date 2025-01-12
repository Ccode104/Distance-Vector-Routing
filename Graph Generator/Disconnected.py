import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
G = nx.Graph()

# Add nodes and edge with weight
edges = [
    ('A', 'B', 5)
]

G.add_weighted_edges_from(edges)
G.add_node('C')
# Draw the graph
pos = nx.spring_layout(G)  # Layout for node positioning
plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=3000, node_color='lightgreen', font_size=12, font_weight='bold', edge_color='gray')

# Draw edge labels (weights)
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

# Show the plot
plt.title("Graph: A, B, C")
plt.show()
