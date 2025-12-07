import gurobipy as gp
from gurobipy import GRB

class MinCostFlowModel:
    def __init__(self):
        self.model = gp.Model("MultiModalTransport")
        self.hubs = []
        self.arcs = []
        self.modes = []
        self.demands = {}
        self.capacities = {}
        self.costs = {}
        self.hub_capacities = {}
        
    def set_data(self, hubs, modes, arcs, demands, capacities, costs, hub_capacities):
        """
        Initialize the model with data.
        
        :param hubs: List of hub names (nodes)
        :param modes: List of transportation modes (e.g., ['Train', 'Bus'])
        :param arcs: List of tuples (origin, destination)
        :param demands: Dict {hub: net_demand} (+ve for supply, -ve for demand)
        :param capacities: Dict {(origin, destination, mode): capacity}
        :param costs: Dict {(origin, destination, mode): unit_cost}
        :param hub_capacities: Dict {hub: max_throughput}
        """
        self.hubs = hubs
        self.modes = modes
        self.arcs = arcs
        self.demands = demands
        self.capacities = capacities
        self.costs = costs
        self.hub_capacities = hub_capacities
        
    def build_model(self):
        """Constructs the variables, objective, and constraints."""
        self.model.reset()
        
        # Decision Variables: Flow on each arc for each mode
        # x[i, j, k] = number of passengers from i to j using mode k
        self.flow = {}
        for i, j in self.arcs:
            for k in self.modes:
                var_name = f"flow_{i}_{j}_{k}"
                self.flow[i, j, k] = self.model.addVar(
                    vtype=GRB.INTEGER, 
                    name=var_name,
                    lb=0
                )
        
        # Objective Function: Minimize Total Cost
        # Sum(cost * flow) for all arcs and modes
        objective_expr = gp.quicksum(
            self.costs.get((i, j, k), 0) * self.flow[i, j, k]
            for i, j in self.arcs for k in self.modes
        )
        self.model.setObjective(objective_expr, GRB.MINIMIZE)
        
        # Constraint 1: Flow Conservation (Balance of Flux)
        # For each node: Sum(Inflow) - Sum(Outflow) = Demand
        # Note: Standard convention is Out - In = Supply. 
        # Let's stick to: Supply (Out - In) = b_i
        # If b_i > 0: Supply (Source), if b_i < 0: Demand (Sink)
        
        for i in self.hubs:
            outflow = gp.quicksum(
                self.flow[i, j, k] 
                for j in self.hubs if (i, j) in self.arcs 
                for k in self.modes
            )
            inflow = gp.quicksum(
                self.flow[j, i, k] 
                for j in self.hubs if (j, i) in self.arcs 
                for k in self.modes
            )
            
            self.model.addConstr(
                outflow - inflow == self.demands.get(i, 0),
                name=f"balance_{i}"
            )
            
        # Constraint 2: Link Capacity (per mode)
        for i, j in self.arcs:
            for k in self.modes:
                cap = self.capacities.get((i, j, k), 0)
                self.model.addConstr(
                    self.flow[i, j, k] <= cap,
                    name=f"cap_{i}_{j}_{k}"
                )

        # Constraint 3: Hub Throughput Capacity
        # Total flow entering a hub (transit + destination) cannot exceed its capacity
        # Or strictly transit? Let's assume Total Inflow <= Hub Capacity for simplicity + realism
        for i in self.hubs:
            if i in self.hub_capacities:
                total_inflow = gp.quicksum(
                    self.flow[j, i, k] 
                    for j in self.hubs if (j, i) in self.arcs 
                    for k in self.modes
                )
                self.model.addConstr(
                    total_inflow <= self.hub_capacities[i],
                    name=f"hub_cap_{i}"
                )

        self.model.update()

    def solve(self):
        """Solves the optimization model."""
        try:
            self.model.optimize()
            
            if self.model.status == GRB.OPTIMAL:
                print(f"Optimal Objective Value: {self.model.objVal}")
                result = {
                    'status': 'Optimal',
                    'objective': self.model.objVal,
                    'flows': {}
                }
                for (i, j, k), var in self.flow.items():
                    if var.x > 0:
                        result['flows'][(i, j, k)] = var.x
                return result
            else:
                return {'status': 'Not Optimal', 'code': self.model.status}
                
        except gp.GurobiError as e:
            print(f"Gurobi Error: {e}")
            return {'status': 'Error', 'message': str(e)}

if __name__ == "__main__":
    # Simple Test Case
    model = MinCostFlowModel()
    
    hubs = ['Paris', 'Lyon', 'Marseille']
    modes = ['Train', 'Bus']
    arcs = [('Paris', 'Lyon'), ('Lyon', 'Marseille'), ('Paris', 'Marseille')]
    
    # Paris supplies 100 passengers, Marseille needs 100
    demands = {'Paris': 100, 'Marseille': -100, 'Lyon': 0}
    
    # Capacities and Costs
    capacities = {
        ('Paris', 'Lyon', 'Train'): 80, ('Paris', 'Lyon', 'Bus'): 50,
        ('Lyon', 'Marseille', 'Train'): 80, ('Lyon', 'Marseille', 'Bus'): 50,
        ('Paris', 'Marseille', 'Train'): 40, ('Paris', 'Marseille', 'Bus'): 20
    }
    
    costs = {
        ('Paris', 'Lyon', 'Train'): 50, ('Paris', 'Lyon', 'Bus'): 20,
        ('Lyon', 'Marseille', 'Train'): 50, ('Lyon', 'Marseille', 'Bus'): 20,
        ('Paris', 'Marseille', 'Train'): 120, ('Paris', 'Marseille', 'Bus'): 60
    }
    
    hub_caps = {'Lyon': 200} # Lyon can handle transit
    
    model.set_data(hubs, modes, arcs, demands, capacities, costs, hub_caps)
    model.build_model()
    res = model.solve()
    print(res)
