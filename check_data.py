import networkx as nx
import os
from backend.graph_logic import build_graph

def check_my_metro_data():
    print("🚀 Đang bắt đầu kiểm tra dữ liệu Metro...")
    
    # 1. Load đồ thị
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'data/metro_rer_idf.csv')
    
    try:
        G = build_graph(csv_path)
    except Exception as e:
        print(f"❌ Lỗi khi nạp file CSV: {e}")
        return

    print(f"📊 Thông tin cơ bản: {G.number_of_nodes()} ga và {G.number_of_edges()} đoạn nối.")

    # 2. Kiểm tra các ga bị cô lập (Isolates)
    isolates = list(nx.isolates(G))
    if isolates:
        print(f"⚠️ Cảnh báo: Có {len(isolates)} ga bị cô lập (không có đường nối):")
        for ga in isolates[:10]: # In thử 10 ga đầu
            print(f"   - {ga}")
        if len(isolates) > 10: print("   ... và nhiều ga khác.")
    else:
        print("✅ Không có ga nào bị cô lập.")

    # 3. Kiểm tra tính liên thông (Connected Components)
    num_components = nx.number_connected_components(G)
    if num_components == 1:
        print("✅ Tuyệt vời: Toàn bộ mạng lưới thông suốt (1 mảnh duy nhất).")
    else:
        print(f"❌ Dữ liệu bị chia cắt thành {num_components} mảnh rời rạc!")
        components = sorted(nx.connected_components(G), key=len, reverse=True)
        print("🔍 Kích thước các mảnh:")
        for i, c in enumerate(components[:5]): # In 5 mảnh lớn nhất
            print(f"   - Mảnh {i+1}: {len(c)} ga")

    print("\n--- Hoàn tất kiểm tra ---")

if __name__ == "__main__":
    check_my_metro_data()