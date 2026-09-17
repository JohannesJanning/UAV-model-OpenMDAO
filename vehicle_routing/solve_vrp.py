from __future__ import annotations

import math
import random
from pathlib import Path

import matplotlib.pyplot as plt
from ortools.constraint_solver import pywrapcp, routing_enums_pb2


X_LIMITS_KM = (-15.0, 15.0)
Y_LIMITS_KM = (-10.0, 10.0)
DEPOT = 0
NUM_VEHICLES = 10
VEHICLE_PAYLOAD_CAPACITY_KG = 10
DEMAND_RANDOM_SEED = 42
OUTPUT_PATH = Path(__file__).with_name("vrp_routes.png")

# Node 0 is the depot. Nodes 1-10 are customer locations in kilometres.
LOCATIONS_KM = (
    (0.0, 0.0),
    (-10.09, 5.34),
    (-7.95, 9.88),
    (-4.60, -8.21),
    (-3.58, 0.88),
    (-2.80, -5.22),
    (2.57, -5.30),
    (4.32, -7.28),
    (4.89, 0.36),
    (13.88, 8.68),
    (14.75, -6.08),
)
customer_demands = [1] * 5 + [2] * 5
random.Random(DEMAND_RANDOM_SEED).shuffle(customer_demands)
DEMANDS = (0, *customer_demands)


def euclidean_distance(first: tuple[float, float], second: tuple[float, float]) -> float:
    return math.hypot(first[0] - second[0], first[1] - second[1])


def solve_routes() -> tuple[pywrapcp.RoutingModel, pywrapcp.RoutingIndexManager, object]:
    manager = pywrapcp.RoutingIndexManager(
        len(LOCATIONS_KM),
        NUM_VEHICLES,
        DEPOT,
    )
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index: int, to_index: int) -> int:
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return round(euclidean_distance(LOCATIONS_KM[from_node], LOCATIONS_KM[to_node]) * 1000)

    distance_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(distance_callback_index)

    def demand_callback(from_index: int) -> int:
        return DEMANDS[manager.IndexToNode(from_index)]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        [VEHICLE_PAYLOAD_CAPACITY_KG] * NUM_VEHICLES,
        True,
        "Capacity",
    )

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = 5

    solution = routing.SolveWithParameters(search_parameters)
    if solution is None:
        raise RuntimeError("OR-Tools did not find a feasible routing solution.")

    return routing, manager, solution


def extract_routes(
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    solution: object,
) -> list[tuple[list[int], float, int]]:
    routes = []
    for vehicle_id in range(NUM_VEHICLES):
        index = routing.Start(vehicle_id)
        route = []
        distance_m = 0
        load = 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(node)
            load += DEMANDS[node]
            next_index = solution.Value(routing.NextVar(index))
            next_node = manager.IndexToNode(next_index)
            distance_m += (
                euclidean_distance(
                    LOCATIONS_KM[node],
                    LOCATIONS_KM[next_node],
                )
                * 1000
            )
            index = next_index

        route.append(manager.IndexToNode(index))
        if len(route) > 2:
            routes.append((route, distance_m / 1000.0, load))

    return routes


def validate_routes(routes: list[tuple[list[int], float, int]]) -> None:
    """Independently verify coverage, depot returns, and payload capacity."""
    visited_customers: list[int] = []

    for route_number, (route, _distance_km, reported_load) in enumerate(routes, start=1):
        if len(route) < 2 or route[0] != DEPOT or route[-1] != DEPOT:
            raise RuntimeError(
                f"Route {route_number} must start and end at depot {DEPOT}: {route}"
            )

        customers = route[1:-1]
        if any(node == DEPOT for node in customers):
            raise RuntimeError(f"Route {route_number} visits the depot mid-route: {route}")

        recomputed_load = sum(DEMANDS[node] for node in customers)
        if recomputed_load != reported_load:
            raise RuntimeError(
                f"Route {route_number} load mismatch: "
                f"reported {reported_load}, computed {recomputed_load}"
            )
        if recomputed_load > VEHICLE_PAYLOAD_CAPACITY_KG:
            raise RuntimeError(
                f"Route {route_number} exceeds capacity: "
                f"{recomputed_load}/{VEHICLE_PAYLOAD_CAPACITY_KG} kg"
            )

        visited_customers.extend(customers)

    expected_customers = set(range(1, len(LOCATIONS_KM)))
    actual_customers = set(visited_customers)
    if actual_customers != expected_customers or len(visited_customers) != len(actual_customers):
        raise RuntimeError(
            "Customer coverage check failed: "
            f"expected {sorted(expected_customers)}, got {visited_customers}"
        )


def plot_routes(routes: list[tuple[list[int], float, int]]) -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman"],
            "font.size": 12,
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
        }
    )
    figure, axis = plt.subplots(figsize=(10, 6), constrained_layout=True)
    colors = ("#1565c0", "#ef6c00", "#2e7d32", "#8e24aa", "#6d4c41")

    for route_number, (route, distance_km, load) in enumerate(routes, start=1):
        x_values = [LOCATIONS_KM[node][0] for node in route]
        y_values = [LOCATIONS_KM[node][1] for node in route]
        axis.plot(
            x_values,
            y_values,
            color=colors[(route_number - 1) % len(colors)],
            linewidth=2.2,
            marker="o",
            markersize=5,
            label=f"Vehicle {route_number}: {distance_km:.1f} km, load {load}",
        )

    customer_x = [location[0] for location in LOCATIONS_KM[1:]]
    customer_y = [location[1] for location in LOCATIONS_KM[1:]]
    axis.scatter(customer_x, customer_y, color="black", s=22, zorder=3)
    for node, (x_value, y_value) in enumerate(LOCATIONS_KM[1:], start=1):
        axis.annotate(
            f"[{DEMANDS[node]}]",
            (x_value, y_value),
            xytext=(0, -8),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=12,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5},
        )

    axis.scatter(
        [LOCATIONS_KM[DEPOT][0]],
        [LOCATIONS_KM[DEPOT][1]],
        color="green",
        marker="s",
        s=90,
        zorder=4,
        label="Depot",
    )
    axis.set_title(f"Vehicle routing solution: 10 customers, {NUM_VEHICLES} vehicles")
    axis.set_xlabel("X coordinate (km)")
    axis.set_ylabel("Y coordinate (km)")
    axis.set_xlim(*X_LIMITS_KM)
    axis.set_ylim(*Y_LIMITS_KM)
    axis.set_aspect("equal", adjustable="box")
    axis.grid(True, alpha=0.25)
    axis.legend(frameon=False, loc="lower left", fontsize=11)
    figure.savefig(OUTPUT_PATH, dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    routing, manager, solution = solve_routes()
    routes = extract_routes(routing, manager, solution)
    validate_routes(routes)
    print("Independent route validation passed.")
    plot_routes(routes)

    print(f"Saved route plot to {OUTPUT_PATH}")
    for route_number, (route, distance_km, load) in enumerate(routes, start=1):
        print(
            f"Vehicle {route_number}: "
            f"{' -> '.join(map(str, route))}; "
            f"distance={distance_km:.2f} km; load={load}/{VEHICLE_PAYLOAD_CAPACITY_KG} kg"
        )


if __name__ == "__main__":
    main()
