import pandas as pd
import networkx as nx
import os



def normalize_station_name(name):
    if not isinstance(name, str):
        return name
    
    name = name.strip()
    
    # Từ điển quy đổi: Cứ thấy tên bên trái thì đổi thành tên bên phải
    mapping = {
        "La Défense Grande Arche": "La Défense (Grande Arche)",
        "La Défense-Grande Arche": "La Défense (Grande Arche)",
        "Charles de Gaulle Etoile": "Charles de Gaulle - Étoile",
        "Châtelet Les Halles": "Châtelet - Les Halles"
    }
    return mapping.get(name, name)

def build_graph(csv_path):
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    # 1. Chuẩn hóa tên ga ngay lập tức
    df['station_clean'] = df['station'].apply(normalize_station_name)
    
    G = nx.Graph()
    
    # 2. Tạo Nodes (Dùng tên đã sạch làm ID)
    # Gom nhóm để lấy tọa độ trung bình cho các ga trùng tên
    coords = df.groupby('station_clean').agg({'latitude': 'mean', 'longitude': 'mean'}).to_dict('index')
    for name, pos in coords.items():
        G.add_node(name, lat=pos['latitude'], lon=pos['longitude'])

    # 3. Tạo Edges (Nối các ga trong cùng một tuyến)
    df = df.sort_values(by=['ligne', 'ordre'])
    for ligne, group in df.groupby('ligne'):
        stations = group['station_clean'].tolist()
        for i in range(len(stations) - 1):
            u, v = stations[i], stations[i+1]
            if u != v:
                # Trọng số = 1 (đi qua 1 trạm), có thể thay bằng khoảng cách thực tế nếu muốn
                G.add_edge(u, v, weight=1, label=ligne)
                
    return G
            

# --- ĐOẠN CODE DƯỚI ĐÂY CHỈ ĐỂ CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    # Tự động tìm đường dẫn tới file CSV trong thư mục data/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(current_dir, '../data/metro_rer_idf.csv')
    
    print("⏳ Đang xây dựng đồ thị mạng lưới Metro...")
    metro_graph = build_graph(csv_file_path)
    
    print(f"✅ Hoàn tất! Đồ thị có {metro_graph.number_of_nodes()} ga và {metro_graph.number_of_edges()} đoạn nối.")
    
    # Thử tìm đường đi (Dựa trên hình ảnh bạn chụp, chọn 2 ga có thật)
    ga_bat_dau = "Auber" 
    ga_ket_thuc = "La Défense" 
    
    print(f"\n🔍 Đang tìm lộ trình ngắn nhất từ '{ga_bat_dau}' đến '{ga_ket_thuc}'...")
    
    try:
        # Gọi thuật toán Dijkstra có sẵn của NetworkX
        duong_di = nx.shortest_path(metro_graph, source=ga_bat_dau, target=ga_ket_thuc, weight='weight')
        
        print("\n🎉 Lộ trình gợi ý:")
        print(" -> ".join(duong_di))
        print(f"Tổng số trạm phải đi qua: {len(duong_di) - 1} trạm")
        
    except nx.NetworkXNoPath:
        print(f"❌ Không tìm thấy đường đi giữa {ga_bat_dau} và {ga_ket_thuc}.")
    except nx.NodeNotFound as e:
        print(f"❌ Lỗi: Không tìm thấy ga. Hãy kiểm tra lại tên ga (có phân biệt hoa/thường). Chi tiết: {e}")


def normalize_station_name(name):
    if not isinstance(name, str): return name
    name = name.strip()
    
    mapping = {
        # Gộp các ga trung tâm để tạo "cầu nối" cho AI
        "Châtelet Les Halles": "Châtelet",
        "Châtelet-Les Halles": "Châtelet",
        "Gare de l'Est (Verdun)": "Gare de l'Est",
        "Gare du Nord (La Chapelle)": "Gare du Nord",
        "Charles de Gaulle Etoile": "Charles de Gaulle – Étoile",
        "Auber": "Auber", # Đảm bảo ga này nối với Opera nếu cần
        "Haussmann Saint-Lazare": "Saint-Lazare",
        "La Défense Grande Arche": "La Défense (Grande Arche)",
    }
    return mapping.get(name, name)


import re

def normalize_station_name(name):
    if not isinstance(name, str): return name
    # Chuyển về chữ thường, xóa khoảng trắng đầu cuối
    name = name.lower().strip()
    # Xóa nội dung trong ngoặc đơn (ví dụ: "Gare de l'Est (Verdun)" -> "Gare de l'Est")
    name = re.sub(r'\(.*\)', '', name).strip()
    # Thay thế các ký tự đặc biệt bằng khoảng trắng để đồng bộ
    name = name.replace('-', ' ').replace('–', ' ').replace("'", " ")
    # Xóa khoảng trắng thừa giữa các từ
    name = " ".join(name.split())
    return name