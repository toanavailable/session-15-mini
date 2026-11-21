"""SkyBooking System - Hệ thống đặt vé máy bay chuyến VN2026."""

# =====================================================================
# DỮ LIỆU TOÀN CỤC (GLOBAL)
# =====================================================================
available_seats = 50        # Số ghế trống
flight_revenue = 0.0        # Tổng doanh thu chuyến bay ($)

BASE_PRICE = 2000.0         # Giá vé cơ bản (hằng số)
MAX_SEATS = 50              # Sức chứa tối đa
BUSINESS_RATE = 1.5         # Vé Business = BASE_PRICE * 1.5
SERVICE_FEE_RATE = 0.05     # Phí dịch vụ sân bay 5%
REFUND_RATE = 0.8           # Hoàn 80% giá vé cơ bản
FLIGHT_CODE = "VN2026"


def read_positive_int(prompt):
    """Nhập số nguyên dương, lặp lại đến khi hợp lệ.

    Tham số:
        prompt (str): câu nhắc nhập liệu
    Trả về:
        int: số nguyên > 0
    """
    while True:
        text = input(prompt).strip()
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Số lượng vé không hợp lệ, vui lòng nhập số nguyên dương!")    # Bẫy 3


def read_ticket_class():
    """Nhập hạng vé, lặp lại đến khi là 1 (Economy) hoặc 2 (Business).

    Trả về:
        int: 1 hoặc 2
    """
    while True:
        text = input("Chọn hạng vé (1: Economy, 2: Business): ").strip()
        if text == "1" or text == "2":
            return int(text)
        print("Hạng vé không hợp lệ, vui lòng chọn 1 hoặc 2!")               # Bẫy 3


def calculate_ticket_cost(quantity, ticket_class):
    """Tính tổng chi phí đặt vé và in phần xác nhận đặt chỗ.

    Tham số:
        quantity (int): số lượng vé
        ticket_class (int): hạng vé, 1 = Economy, 2 = Business
    Trả về:
        float: tổng thanh toán = số vé * giá vé + 5% phí dịch vụ sân bay
    """
    if ticket_class == 1:
        ticket_price = BASE_PRICE                       # biến cục bộ
        class_name = "Economy"
    else:
        ticket_price = BASE_PRICE * BUSINESS_RATE
        class_name = "Business"
    subtotal = quantity * ticket_price                  # biến cục bộ
    service_fee = round(subtotal * SERVICE_FEE_RATE, 2) # biến cục bộ
    total_cost = subtotal + service_fee                 # biến cục bộ

    print("-> Xác nhận đặt chỗ:")
    print(f"Số lượng: {quantity} | Hạng: {class_name}")
    print(f"Tạm tính: ${subtotal}")
    print(f"Phí dịch vụ (5%): ${service_fee}")
    print(f"Tổng thanh toán: ${total_cost}")
    return total_cost


def process_booking(quantity, total_cost):
    """Xử lý đặt vé: trừ ghế trống, cộng doanh thu.

    Tham số:
        quantity (int): số vé đặt
        total_cost (float): số tiền nhận từ calculate_ticket_cost
    Trả về:
        bool: True nếu đặt thành công, False nếu không đủ ghế
    """
    global available_seats, flight_revenue
    if quantity > available_seats:
        print(f"Rất tiếc, chuyến bay chỉ còn {available_seats} chỗ trống.")
        return False
    available_seats -= quantity
    flight_revenue += total_cost
    print(f"Đặt vé thành công! Ghế trống còn lại: {available_seats}")
    return True


def refund_tickets(quantity):
    """Hủy vé và hoàn tiền 80% giá vé cơ bản cho mỗi vé (không hoàn phí dịch vụ).

    Tham số:
        quantity (int): số vé muốn hủy
    Trả về:
        float: số tiền đã hoàn; -1.0 nếu số vé hủy vượt quá số vé đã bán
    """
    global available_seats, flight_revenue
    if available_seats + quantity > MAX_SEATS:
        return -1.0                                     # Bẫy 2: hủy khống
    refund_amount = quantity * BASE_PRICE * REFUND_RATE # biến cục bộ
    available_seats += quantity
    flight_revenue -= refund_amount
    return refund_amount


def show_flight_status():
    """In báo cáo tình trạng chuyến bay.

    Định dạng báo cáo:
        --- TÌNH TRẠNG CHUYẾN BAY VN2026 ---
        Sức chứa tối đa: <MAX_SEATS>
        Ghế đã đặt: <MAX_SEATS - available_seats>
        Ghế trống: <available_seats>
        Tổng doanh thu hiện tại: $<flight_revenue>
    Tham số: không có (chỉ đọc dữ liệu toàn cục). Trả về: None.
    """
    print(f"--- TÌNH TRẠNG CHUYẾN BAY {FLIGHT_CODE} ---")
    print(f"Sức chứa tối đa: {MAX_SEATS}")
    print(f"Ghế đã đặt: {MAX_SEATS - available_seats}")
    print(f"Ghế trống: {available_seats}")
    print(f"Tổng doanh thu hiện tại: ${round(flight_revenue, 2)}")


def main():
    """Vòng lặp chính của hệ thống SkyBooking."""
    while True:
        print("\n============= SKYBOOKING SYSTEM =============")
        print(f"Chuyến bay: {FLIGHT_CODE} | Khởi hành: Hà Nội")
        print("1. Đặt vé máy bay")
        print("2. Hủy vé & Hoàn tiền")
        print("3. Xem tình trạng chuyến bay")
        print("4. Đóng hệ thống")
        print("=" * 45)
        choice = input("Chọn chức năng (1-4): ").strip()

        if choice == "1":
            print("--- ĐẶT VÉ MÁY BAY ---")
            quantity = read_positive_int("Nhập số lượng vé: ")
            if quantity > available_seats:                       # Bẫy 1: từ chối ngay
                print(f"Rất tiếc, chuyến bay chỉ còn {available_seats} chỗ trống.")
                continue
            ticket_class = read_ticket_class()
            total_cost = calculate_ticket_cost(quantity, ticket_class)  # trả về tiền
            process_booking(quantity, total_cost)                       # nhận tiền, cập nhật global

        elif choice == "2":
            print("--- HỦY VÉ & HOÀN TIỀN ---")
            quantity = read_positive_int("Nhập số lượng vé muốn hủy: ")
            refund_amount = refund_tickets(quantity)
            if refund_amount < 0:
                print("Lỗi: Số lượng vé hủy vượt quá số vé đã bán ra.")
            else:
                print(f"Hủy vé thành công. Hệ thống đã hoàn lại: ${refund_amount} (80% giá cơ bản).")
                print(f"Ghế trống hiện tại: {available_seats}")

        elif choice == "3":
            show_flight_status()

        elif choice == "4":
            print("Đã đóng hệ thống SkyBooking. Kết thúc phiên làm việc!")
            break

        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!")


if __name__ == "__main__":
    main()
