from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import networkx as nx
import os
import math  # 1. Thêm thư viện toán học để tính khoảng cách
from backend.graph_logic import build_graph

app = FastAPI(title="Paris Metro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

metro_graph = None

@app.on_event("startup")
async def startup_event():
    global metro_graph
    print("⏳ Đang nạp bản đồ Metro vào bộ nhớ...")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, '../data/metro_rer_idf.csv')
    metro_graph = build_graph(csv_file_path)
    print("✅ API đã sẵn sàng nhận yêu cầu!")

# --- 2. THÊM HÀM LA BÀN (HEURISTIC) CHO A* ---
def la_ban_heuristic(ga_hien_tai, ga_dich):
    """
    Tính khoảng cách đường chim bay giữa ga hiện tại đang xét và ga đích.
    A* sẽ dùng con số này để biết nó có đang đi đúng hướng hay không.
    """
    lat1 = metro_graph.nodes[ga_hien_tai]['lat']
    lon1 = metro_graph.nodes[ga_hien_tai]['lon']
    lat2 = metro_graph.nodes[ga_dich]['lat']
    lon2 = metro_graph.nodes[ga_dich]['lon']
    
    # Dùng định lý Pytago để tính khoảng cách tương đối dựa trên tọa độ
    khoang_cach = math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)
    return khoang_cach

@app.get("/api/find-route")
async def find_route(start: str, end: str):
    if start not in metro_graph.nodes:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy ga xuất phát: {start}")
    if end not in metro_graph.nodes:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy ga đích: {end}")
    
    try:
        # --- 3. ĐỔI TỪ SHORTEST_PATH SANG ASTAR_PATH ---
        path = nx.astar_path(
            metro_graph, 
            source=start, 
            target=end, 
            heuristic=la_ban_heuristic, # Truyền hàm la bàn vào đây
            weight='weight'
        )
        
        route_details = []
        for station in path:
            node_data = metro_graph.nodes[station]
            route_details.append({
                "station": station,
                "lat": node_data['lat'],
                "lon": node_data['lon']
            })
            
        return {
            "success": True,
            "total_stops": len(path) - 1,
            "route": route_details
        }
        
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=404, detail="Không có tuyến đường nào kết nối hai ga này.")

# --- ENDPOINT LẤY DANH SÁCH TẤT CẢ CÁC GA ---
@app.get("/api/stations")
async def get_all_stations():
    # Lấy toàn bộ tên ga (Nodes) từ đồ thị và chuyển thành danh sách (list)
    if metro_graph is None:
        raise HTTPException(status_code=500, detail="Bản đồ chưa sẵn sàng")
    
    danh_sach_ga = list(metro_graph.nodes)
    return {"stations": danh_sach_ga}

# ... (Hàm @app.get("/api/find-route") cũ giữ nguyên ở dưới) ...