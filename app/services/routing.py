import networkx as nx
from sqlalchemy.orm import Session
from app.models import Ward, TrafficData

def optimize_routes(db: Session):
    """
    Uses NetworkX to simulate route optimization.
    Given traffic congestion (from TrafficData), computes optimal diversion routes.
    """
    wards = db.query(Ward).all()
    if not wards or len(wards) < 2:
        return {"routes": "Not enough wards to build a graph."}

    # 1. Build a synthetic graph of wards (simulating neighboring wards)
    G = nx.Graph()
    for w in wards:
        G.add_node(w.id, name=w.name)
        
    # Connect wards sequentially as a basic ring/grid for simulation
    for i in range(len(wards)):
        w1 = wards[i]
        w2 = wards[(i+1) % len(wards)]
        G.add_edge(w1.id, w2.id, weight=1.0)
        
        if i + 2 < len(wards):
            w3 = wards[(i+2) % len(wards)]
            G.add_edge(w1.id, w3.id, weight=1.5)

    # 2. Update edge weights based on latest traffic density
    for u, v, data in G.edges(data=True):
        # Fetch traffic for nodes
        t_u = db.query(TrafficData).filter(TrafficData.ward_id == u).order_by(TrafficData.timestamp.desc()).first()
        t_v = db.query(TrafficData).filter(TrafficData.ward_id == v).order_by(TrafficData.timestamp.desc()).first()
        
        # Add a penalty to the weight if density is high
        penalty = 0
        if t_u and t_u.traffic_density > 0.6:
            penalty += t_u.traffic_density * 5
        if t_v and t_v.traffic_density > 0.6:
            penalty += t_v.traffic_density * 5
            
        data['weight'] = data['weight'] + penalty

    # 3. Pick a random start and end point to compute the optimal route avoiding congestion
    import random
    if len(wards) >= 2:
        nodes = list(G.nodes)
        source, target = random.sample(nodes, 2)
        try:
            path = nx.dijkstra_path(G, source, target, weight='weight')
            return {
                "source_node": source,
                "target_node": target,
                "optimal_path": path,
                "message": "Route heavily avoids congested wards."
            }
        except nx.NetworkXNoPath:
            return {"error": "No path found."}
            
    return {"message": "Graph too small"}
