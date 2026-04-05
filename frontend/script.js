// 1. Khởi tạo bản đồ, lấy tâm là thành phố Paris
// Thêm { zoomControl: false } để tắt nút zoom mặc định ở góc trái
const map = L.map('map', { zoomControl: false }).setView([48.8566, 2.3522], 12);

// Sau đó tự thêm lại nút zoom vào góc dưới bên phải (bottomright) cho giống Google Maps
L.control.zoom({
    position: 'bottomright'
}).addTo(map);


// Biến lưu trữ toàn bộ tên ga lấy từ Server
let allStations = [];

// Hàm tải danh sách ga khi trang web vừa mở
async function loadStations() {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/stations');
        const data = await response.json();
        allStations = data.stations;
    } catch (error) {
        console.error("Lỗi khi tải danh sách ga:", error);
    }
}
loadStations(); // Gọi hàm ngay lập tức

// Hàm tạo tính năng Auto-complete
function setupAutocomplete(inputId, suggestionBoxId) {
    const input = document.getElementById(inputId);
    const suggestionBox = document.getElementById(suggestionBoxId);

    // Bắt sự kiện mỗi khi người dùng gõ phím
    input.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        suggestionBox.innerHTML = ''; // Xóa các gợi ý cũ

        if (!query) {
            suggestionBox.style.display = 'none'; // Nếu xóa hết chữ thì ẩn gợi ý
            return;
        }

        // Lọc các ga có chứa từ khóa vừa gõ
        const filtered = allStations.filter(station => station.toLowerCase().startsWith(query));

        if (filtered.length > 0) {
            suggestionBox.style.display = 'block'; // Hiện khung gợi ý
            
            filtered.forEach(station => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = station;
                
                // Khi click vào 1 gợi ý
                div.onclick = function() {
                    input.value = station; // Điền tên ga chuẩn vào ô
                    suggestionBox.style.display = 'none'; // Ẩn khung gợi ý đi
                };
                
                suggestionBox.appendChild(div);
            });
        } else {
            suggestionBox.style.display = 'none';
        }
    });

    // Ẩn khung gợi ý khi bấm chuột ra ngoài ô nhập liệu
    document.addEventListener('click', function(e) {
        if (e.target !== input && e.target !== suggestionBox) {
            suggestionBox.style.display = 'none';
        }
    });
}

// Kích hoạt tính năng cho cả 2 ô
setupAutocomplete('start-station', 'start-suggestions');
setupAutocomplete('end-station', 'end-suggestions');

// 2. Thêm lớp bản đồ đường phố từ OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Biến lưu trữ tuyến đường đang vẽ để xóa đi khi tìm đường mới
let currentRouteLayer = null;
let currentMarkers = [];

async function findRoute() {
    const start = document.getElementById('start-station').value;
    const end = document.getElementById('end-station').value;
    const statusDiv = document.getElementById('status-message');

    if (!start || !end) {
        statusDiv.innerHTML = "<span style='color:red;'>Vui lòng nhập đủ 2 ga!</span>";
        return;
    }

    statusDiv.innerHTML = "⏳ Đang nhờ AI tìm đường...";

    try {
        // Gọi API đến Backend FastAPI của bạn
        const response = await fetch(`http://127.0.0.1:8000/api/find-route?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Lỗi không xác định từ Server");
        }

        // Xóa đường vẽ và marker cũ (nếu có)
        if (currentRouteLayer) map.removeLayer(currentRouteLayer);
        currentMarkers.forEach(marker => map.removeLayer(marker));
        currentMarkers = [];

        // Trích xuất mảng tọa độ từ dữ liệu AI trả về
        const routeCoords = data.route.map(station => [station.lat, station.lon]);

        // Vẽ đường đi (Polyline) màu xanh dương đậm, nét dày
        currentRouteLayer = L.polyline(routeCoords, {
            color: '#1a73e8',
            weight: 6,
            opacity: 0.8
        }).addTo(map);

        // Đánh dấu (Marker) cho ga Đi và ga Đến
        const startStation = data.route[0];
        const endStation = data.route[data.route.length - 1];

        const startMarker = L.marker([startStation.lat, startStation.lon]).bindPopup(`<b>Xuất phát:</b> ${startStation.station}`).addTo(map);
        const endMarker = L.marker([endStation.lat, endStation.lon]).bindPopup(`<b>Đích đến:</b> ${endStation.station}`).addTo(map);
        
        currentMarkers.push(startMarker, endMarker);

        // Tự động zoom và dịch chuyển bản đồ sao cho hiển thị vừa vặn toàn bộ tuyến đường
        map.fitBounds(currentRouteLayer.getBounds(), { padding: [50, 50] });

        statusDiv.innerHTML = `<span style='color:green;'>✅ Tìm thấy! Cần đi qua ${data.total_stops} trạm.</span>`;

    } catch (error) {
        statusDiv.innerHTML = `<span style='color:red;'>❌ ${error.message}</span>`;
    }
}