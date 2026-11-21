# Bài 3 - Hệ thống đặt vé máy bay (SkyBooking System)

## Đề bài

Hãng hàng không quản lý bán vé chuyến **VN2026**, theo dõi chính xác **số ghế trống** và **tổng doanh thu** theo thời gian thực, tránh lỗi overbooking (bán vượt số ghế). Dữ liệu toàn cục: `available_seats = 50`, `flight_revenue = 0.0`, hằng số `BASE_PRICE = 2000.0`. Sinh viên tự thiết kế tên hàm và cách truyền dữ liệu.

### Menu

```
============= SKYBOOKING SYSTEM =============
Chuyến bay: VN2026 | Khởi hành: Hà Nội
1. Đặt vé máy bay
2. Hủy vé & Hoàn tiền
3. Xem tình trạng chuyến bay
4. Đóng hệ thống
=============================================
Chọn chức năng (1-4):
```

### Yêu cầu chức năng

| Chức năng | Hàm | Mô tả |
|---|---|---|
| 1. Đặt vé | `calculate_ticket_cost(quantity, ticket_class)` → `process_booking(quantity, total_cost)` | Economy = BASE_PRICE, Business = BASE_PRICE × 1.5; cộng 5% phí dịch vụ; `return` tổng tiền. Hàm đặt vé kiểm tra ghế, dùng `global` trừ ghế và cộng doanh thu |
| 2. Hủy vé | `refund_tickets(quantity)` | Hoàn 80% BASE_PRICE mỗi vé (không hoàn phí dịch vụ); ghế sau hủy không vượt 50; `return` số tiền hoàn |
| 3. Tình trạng | `show_flight_status()` | Có docstring mô tả định dạng báo cáo |
| 4. Đóng hệ thống | `main()` | Thông báo kết thúc phiên làm việc |

### Edge cases

| Bẫy | Tình huống | Xử lý |
|---|---|---|
| Bẫy 1 - Overbooking | Số vé > ghế trống | Từ chối ngay sau khi nhập số lượng: "Rất tiếc, chuyến bay chỉ còn [X] chỗ trống." |
| Bẫy 2 - Hủy khống | Ghế trống + số vé hủy > 50 | "Lỗi: Số lượng vé hủy vượt quá số vé đã bán ra." |
| Bẫy 3 - Dữ liệu rác | Hạng vé khác 1/2; số lượng âm, 0 hoặc chữ | Báo lỗi và yêu cầu nhập lại |

## (1) Phân tích và thiết kế

### Sơ đồ luồng dữ liệu (dòng chảy giá trị tiền tệ)

```
 main()
   │  quantity, ticket_class  (nhập + kiểm tra bằng read_positive_int / read_ticket_class)
   ▼
 calculate_ticket_cost(quantity, ticket_class)          [chỉ dùng biến local + hằng số]
   │  ticket_price ← BASE_PRICE hoặc BASE_PRICE × 1.5
   │  subtotal ← quantity × ticket_price
   │  service_fee ← subtotal × 5%
   │  return total_cost = subtotal + service_fee   ──────┐
   ▼                                                      │ (float)
 process_booking(quantity, total_cost)  ◄────────────────┘
   │  global available_seats −= quantity
   │  global flight_revenue  += total_cost
   ▼
 show_flight_status()  đọc available_seats, flight_revenue để báo cáo

 refund_tickets(quantity):
   refund_amount ← quantity × BASE_PRICE × 80%
   global available_seats += quantity ; global flight_revenue −= refund_amount
   return refund_amount → main() in ra màn hình
```

### Tính toàn vẹn dữ liệu: vì sao doanh thu phải là biến toàn cục?

- Doanh thu là **trạng thái chung của chuyến bay**, được cộng ở chức năng đặt vé, trừ ở chức năng hủy vé và đọc ở chức năng báo cáo. Nếu là biến cục bộ, nó sẽ **mất đi khi hàm kết thúc**: mỗi lần đặt vé lại bắt đầu từ 0, báo cáo sẽ luôn sai.
- Chỉ có **một nguồn dữ liệu duy nhất** (`flight_revenue`, `available_seats`) mà mọi chức năng cùng cập nhật, nên số ghế và doanh thu luôn khớp nhau. Đây chính là điều kiện để không xảy ra overbooking.
- Ngược lại, các con số của một lần đặt vé (giá vé, tạm tính, phí dịch vụ) là **biến cục bộ** trong `calculate_ticket_cost`. Hàm này chỉ trả kết quả ra ngoài và không tự sửa dữ liệu chung, nên tính sai một lần cũng không làm hỏng trạng thái chuyến bay.

### Danh sách hàm

| Hàm | Input | Output | Global |
|---|---|---|---|
| `read_positive_int(prompt)` | str | `int` > 0 | Không |
| `read_ticket_class()` | không | `int` 1 hoặc 2 | Không |
| `calculate_ticket_cost(quantity, ticket_class)` | int, int | `float` tổng tiền | Chỉ đọc hằng số |
| `process_booking(quantity, total_cost)` | int, float | `bool` | **Sửa** ghế, doanh thu |
| `refund_tickets(quantity)` | int | `float` tiền hoàn (−1.0 nếu lỗi) | **Sửa** ghế, doanh thu |
| `show_flight_status()` | không | `None` | Chỉ đọc |
| `main()` | không | `None` | Chỉ đọc `available_seats` để chặn overbooking sớm |

## (2) Triển khai code

File: [`sky_booking.py`](sky_booking.py)

```python
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
```

## Kết quả

```
Chọn chức năng (1-4): 2
--- HỦY VÉ & HOÀN TIỀN ---
Nhập số lượng vé muốn hủy: 3
Lỗi: Số lượng vé hủy vượt quá số vé đã bán ra.

Chọn chức năng (1-4): 1
--- ĐẶT VÉ MÁY BAY ---
Nhập số lượng vé: 2
Chọn hạng vé (1: Economy, 2: Business): 2
-> Xác nhận đặt chỗ:
Số lượng: 2 | Hạng: Business
Tạm tính: $6000.0
Phí dịch vụ (5%): $300.0
Tổng thanh toán: $6300.0
Đặt vé thành công! Ghế trống còn lại: 48

Chọn chức năng (1-4): 2
--- HỦY VÉ & HOÀN TIỀN ---
Nhập số lượng vé muốn hủy: 1
Hủy vé thành công. Hệ thống đã hoàn lại: $1600.0 (80% giá cơ bản).
Ghế trống hiện tại: 49

Chọn chức năng (1-4): 3
--- TÌNH TRẠNG CHUYẾN BAY VN2026 ---
Sức chứa tối đa: 50
Ghế đã đặt: 1
Ghế trống: 49
Tổng doanh thu hiện tại: $4700.0

Chọn chức năng (1-4): 1
--- ĐẶT VÉ MÁY BAY ---
Nhập số lượng vé: 0
Số lượng vé không hợp lệ, vui lòng nhập số nguyên dương!
Nhập số lượng vé: -1
Số lượng vé không hợp lệ, vui lòng nhập số nguyên dương!
Nhập số lượng vé: abc
Số lượng vé không hợp lệ, vui lòng nhập số nguyên dương!
Nhập số lượng vé: 3
Chọn hạng vé (1: Economy, 2: Business): 3
Hạng vé không hợp lệ, vui lòng chọn 1 hoặc 2!
Chọn hạng vé (1: Economy, 2: Business): 1
-> Xác nhận đặt chỗ:
Số lượng: 3 | Hạng: Economy
Tạm tính: $6000.0
Phí dịch vụ (5%): $300.0
Tổng thanh toán: $6300.0
Đặt vé thành công! Ghế trống còn lại: 46

Chọn chức năng (1-4): 1
--- ĐẶT VÉ MÁY BAY ---
Nhập số lượng vé: 60
Rất tiếc, chuyến bay chỉ còn 46 chỗ trống.

Chọn chức năng (1-4): 2
--- HỦY VÉ & HOÀN TIỀN ---
Nhập số lượng vé muốn hủy: 5
Lỗi: Số lượng vé hủy vượt quá số vé đã bán ra.

Chọn chức năng (1-4): 1
--- ĐẶT VÉ MÁY BAY ---
Nhập số lượng vé: 47
Rất tiếc, chuyến bay chỉ còn 46 chỗ trống.

Chọn chức năng (1-4): 1
--- ĐẶT VÉ MÁY BAY ---
Nhập số lượng vé: 3
Chọn hạng vé (1: Economy, 2: Business): 2
-> Xác nhận đặt chỗ:
Số lượng: 3 | Hạng: Business
Tạm tính: $9000.0
Phí dịch vụ (5%): $450.0
Tổng thanh toán: $9450.0
Đặt vé thành công! Ghế trống còn lại: 43

Chọn chức năng (1-4): 10
Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!

Chọn chức năng (1-4): 2
--- HỦY VÉ & HOÀN TIỀN ---
Nhập số lượng vé muốn hủy: 45
Lỗi: Số lượng vé hủy vượt quá số vé đã bán ra.

Chọn chức năng (1-4): 3
--- TÌNH TRẠNG CHUYẾN BAY VN2026 ---
Sức chứa tối đa: 50
Ghế đã đặt: 7
Ghế trống: 43
Tổng doanh thu hiện tại: $20450.0

Chọn chức năng (1-4): 9
Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!

Chọn chức năng (1-4): 4
Đã đóng hệ thống SkyBooking. Kết thúc phiên làm việc!
```

### Bảng kiểm thử

| Kịch bản | Dữ liệu | Kết quả |
|---|---|---|
| Bẫy 2 - hủy khi chưa bán vé | Hủy 3 | Lỗi: Số lượng vé hủy vượt quá số vé đã bán ra. |
| Đặt Business | 2 vé hạng 2 | Tạm tính 6000, phí 300, tổng $6300.0, còn 48 ghế (khớp đề) |
| Hủy vé | 1 vé | Hoàn $1600.0, ghế trống 49 (khớp đề) |
| Tình trạng | Chọn 3 | Đã đặt 1, trống 49, doanh thu $4700.0 (khớp đề) |
| Bẫy 3 - số lượng rác | `0`, `-1`, `abc` | Báo lỗi, nhập lại |
| Bẫy 3 - hạng vé sai | `3` | Báo lỗi, chọn lại |
| Đặt Economy | 3 vé hạng 1 | Tổng $6300.0, còn 46 ghế |
| Bẫy 1 - Overbooking | 60, 47 (còn 46) | Rất tiếc, chuyến bay chỉ còn 46 chỗ trống. |
| Bẫy 2 - hủy vượt số đã bán | Hủy 5 (đã bán 4); hủy 45 (đã bán 7) | Lỗi: Số lượng vé hủy vượt quá... |
| Tình trạng cuối | Chọn 3 | Đã đặt 7, trống 43, doanh thu $20450.0 |
| Menu sai / đóng | `10`, `9`, `4` | Báo lỗi / kết thúc phiên |

## Ghi chú

- Overbooking được chặn **ngay sau khi nhập số lượng vé** (trước khi hỏi hạng vé), đúng yêu cầu "từ chối ngay lập tức". `process_booking` vẫn kiểm tra lại số ghế để hàm an toàn khi được gọi từ nơi khác.
- Hủy vé chỉ hoàn 80% giá vé cơ bản ($2000) dù vé là Business, theo đúng chính sách của đề, nên doanh thu còn lại gồm cả phí dịch vụ và phần chênh lệch không hoàn.
