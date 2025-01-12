import threading
import time
import queue
import sys
from datetime import datetime

class Router(threading.Thread):
    def __init__(self, name, neighbors, shared_queue, all_routers, convergence_flag):
        super().__init__()
        self.name = name
        self.neighbors = neighbors  # {neighbor: cost}
        self.shared_queue = shared_queue
        self.routing_table = {router: float('inf') for router in all_routers}  # Initialize all costs as infinity
        self.routing_table[self.name] = 0  # Cost to itself is 0
        self.updated = set()  # Track updated entries
        self.convergence_flag = convergence_flag  # Shared convergence flag

        for neighbor, cost in self.neighbors.items():
            self.routing_table[neighbor] = cost
        
        # File to log outputs for this router
        self.log_file = f"{self.name}_output.txt"

        # Clear any existing content in the log file
        with open(self.log_file, "w") as f:
            f.write(f"Router {self.name} Log\n")
            f.write("=" * 20 + "\n")

    def run(self):
        iteration=0
        while True:
            self.log(f"Router {self.name} running iteration {iteration}")
            self.log_routing_table()

            # Broadcast the table unconditionally in the first iteration or if updates were made
            self.broadcast_table()
            
            time.sleep(2)  # Wait for updates from all neighbors
            self.update_routing_table()

            # Check if convergence has occurred: no updates were made in this iteration
            if not self.updated:
                self.convergence_flag[self.name] = True  # Mark this router as converged

            # If all routers have converged, terminate the simulation
            if all(self.convergence_flag.values()):
                break

            self.updated.clear()  # Reset updated for the next iteration
            iteration+=1

    def broadcast_table(self):
        for neighbor in self.neighbors:
            self.shared_queue.put((self.name, neighbor, self.routing_table))

    def update_routing_table(self):
        while not self.shared_queue.empty():
            sender, receiver, table = self.shared_queue.get()
            if receiver == self.name:
                # Log receipt of distance vector
                self.log(f"Received distance vector from {sender}")

                if sender not in self.routing_table:
                    self.log(f"Error: Sender '{sender}' not found in routing table of router '{self.name}'")
                else:
                    updated = False  # Track if there are updates in this iteration
                    for dest, cost in table.items():
                        # Calculate the new cost to the destination
                        new_cost = self.routing_table[sender] + cost
                        current_cost = self.routing_table.get(dest, float('inf'))

                        # Log calculation details
                        self.log(
                            f"Calculating cost to {dest}: current cost = {current_cost}, "
                            f"new cost via {sender} = {self.routing_table[sender]} + {cost} = {new_cost}"
                        )

                        # Only update if the destination is reachable and the new cost is better
                        if new_cost < current_cost:
                            self.routing_table[dest] = new_cost
                            self.updated.add(dest)  # Mark destination as updated
                            updated = True
                            self.log(f"Updated cost to {dest}: {current_cost} -> {new_cost}")
                        elif current_cost == float('inf'):
                            # If the current cost is infinity, it indicates a disconnected router
                            self.log(f"Dest {dest} remains unreachable for {self.name}")
                    
                    # If there were any updates, broadcast the table
                    if updated:
                        self.broadcast_table()

    def log_routing_table(self):
        self.log("Routing Table:")
        for dest, cost in self.routing_table.items():
            update_flag = "*" if dest in self.updated else ""
            self.log(f"  {dest}: {cost} {update_flag}")
        self.updated.clear()  # Clear the updated set after logging

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

# Parses the input to get the info about the network
def parse_input(file_path):
    with open(file_path, "r") as file:
        lines = file.read().splitlines()
    num_routers = int(lines[0])
    routers = lines[1].split()
    links = [line.split() for line in lines[2:-1]]
    return num_routers, routers, links

# Creates a graph (adjacency matrix representation) for the network
def create_network(topology_file):
    # Get the number of nodes(routers),router names, and the number of links
    num_routers, routers, links = parse_input(topology_file)

    # Create a shared queue
    shared_queue = queue.Queue()
    router_objects = []
    convergence_flag = {router: False for router in routers}  # Shared convergence flag

    # Map each node with its neighbors
    neighbors = {router: {} for router in routers}

    # Fill in the adjacency matrix
    for link in links:
        r1, r2, cost = link[0], link[1], int(link[2])
        neighbors[r1][r2] = cost
        neighbors[r2][r1] = cost

    # Make a list of router objects
    for router in routers:
        router_objects.append(Router(router, neighbors[router], shared_queue, routers, convergence_flag))

    return router_objects, convergence_flag


def main():
    # Check if the command line argument is in correct format
    if len(sys.argv) != 2:
        print("Usage: python <roll_no>_dvr.py <topology_file>")
        sys.exit(1)

    # Read the topology file
    topology_file = sys.argv[1]

    # Create a graph(i.e the network)
    routers, convergence_flag = create_network(topology_file)

    # Start the routers
    for router in routers:
        router.start()

    # Wait until all routers have converged
    for router in routers:
        router.join()

    print("All routers have converged. Terminating simulation.")

if __name__ == "__main__":
    main()
