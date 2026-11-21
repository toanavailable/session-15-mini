"""TechStore Inventory - Hệ thống quản lý kho hàng và doanh thu."""

# =====================================================================
# BIẾN TOÀN CỤC (GLOBAL): trạng thái dùng chung của cả chương trình
# =====================================================================
inventory_stock = 100       # Số lượng sản phẩm trong kho
total_revenue = 0.0         # Tổng doanh thu ($)

DISCOUNT_THRESHOLD = 1000   # Tạm tính từ $1000 trở lên được giảm giá
DISCOUNT_RATE = 0.10        # Giảm 10%
VAT_RATE = 0.08             # Thuế VAT 8%


def read_positive_number(prompt, allow_decimal):
    """Nhập một số dương từ bàn phím.

    Tham số:
        prompt (str): câu nhắc nhập liệu
        allow_decimal (bool): True cho phép số thập phân (đơn giá), False chỉ nhận số nguyên
    Trả về:
        int / float nếu hợp lệ, None nếu không hợp lệ (đã in thông báo lỗi)
    """
    text = input(prompt).strip()
    digits = text[1:] if text.startswith("-") else text     # tách dấu âm để nhận diện số âm
    if allow_decimal:
        digits = digits.replace(".", "", 1)
    if not digits.isdigit():
        print("Lỗi: Vui lòng nhập số hợp lệ (số lượng là số nguyên)!")  # Bẫy 2
        return None
    value = float(text) if allow_decimal else int(text)
    if value <= 0:
        print("Dữ liệu nhập vào phải lớn hơn 0.")                       # Bẫy 1
        return None
    return value


def add_stock(amount):
    """Cộng thêm hàng vào kho.

    Tham số:
        amount (int): số lượng sản phẩm nhập thêm (> 0)
    Trả về:
        int: tồn kho mới sau khi nhập
    """
    global inventory_stock                  # sửa biến toàn cục -> bắt buộc khai báo global
    inventory_stock += amount
    return inventory_stock


def process_sale(quantity):
    """Kiểm tra tồn kho có đủ để bán hay không (chỉ đọc biến toàn cục, không sửa).

    Tham số:
        quantity (int): số lượng khách muốn mua
    Trả về:
        bool: True nếu đủ hàng, False nếu không đủ (đã in thông báo lỗi)
    """
    if quantity > inventory_stock:
        print(f"Lỗi: Không đủ hàng trong kho. Tồn kho hiện tại chỉ còn {inventory_stock}.")
        return False
    return True


def calculate_final_price(quantity, price):
    """Tính tổng tiền đơn hàng và in hóa đơn chi tiết.

    Tham số:
        quantity (int): số lượng mua
        price (float): đơn giá một sản phẩm ($)
    Trả về:
        float: tổng thanh toán = (tạm tính - giảm giá) + 8% VAT
    """
    subtotal = quantity * price                         # biến cục bộ
    discount = 0.0                                      # biến cục bộ
    discount_label = "0%"
    if subtotal >= DISCOUNT_THRESHOLD:
        discount = subtotal * DISCOUNT_RATE
        discount_label = "10%"
    vat = round((subtotal - discount) * VAT_RATE, 2)    # biến cục bộ
    final_total = round(subtotal - discount + vat, 2)   # biến cục bộ

    print("-> Hóa đơn chi tiết:")
    print(f"Số lượng: {quantity} | Đơn giá: ${price}")
    print(f"Tạm tính: ${subtotal}")
    print(f"Giảm giá ({discount_label}): ${discount}")
    print(f"Thuế VAT (8%): ${vat}")
    print(f"Tổng thanh toán: ${final_total}")
    return final_total


def complete_sale(quantity, final_total):
    """Hoàn tất giao dịch: trừ kho và ghi nhận doanh thu.

    Tham số:
        quantity (int): số lượng đã bán
        final_total (float): số tiền thu được của đơn hàng
    Trả về:
        None
    """
    global inventory_stock, total_revenue
    inventory_stock -= quantity
    total_revenue += final_total
    print("Đã bán thành công!")


def print_report():
    """In báo cáo kinh doanh tổng quan.

    Đọc hai biến toàn cục inventory_stock và total_revenue rồi in ra:
    tồn kho hiện tại (sản phẩm) và tổng doanh thu ($).
    Tham số: không có. Trả về: None.
    """
    print("--- BÁO CÁO KINH DOANH ---")
    print(f"Tồn kho hiện tại: {inventory_stock} sản phẩm")
    print(f"Tổng doanh thu: ${round(total_revenue, 2)}")


def main():
    """Vòng lặp menu chính, điều hướng tới các chức năng."""
    while True:
        print("\n========== TECHSTORE MANAGEMENT SYSTEM ==========")
        print("1. Nhập thêm hàng vào kho")
        print("2. Bán hàng (Tính toán hóa đơn)")
        print("3. Xem báo cáo tổng quan")
        print("4. Thoát chương trình")
        print("=" * 49)
        choice = input("Chọn chức năng (1-4): ").strip()

        if choice == "1":
            print("--- NHẬP HÀNG ---")
            amount = read_positive_number("Nhập số lượng sản phẩm muốn thêm: ", False)
            if amount is not None:
                new_stock = add_stock(amount)
                print(f"Đã nhập thành công {amount} sản phẩm.")
                print(f"Tồn kho hiện tại: {new_stock}")

        elif choice == "2":
            print("--- BÁN HÀNG ---")
            quantity = read_positive_number("Nhập số lượng mua: ", False)
            if quantity is None:
                continue
            price = read_positive_number("Nhập đơn giá ($): ", True)
            if price is None:
                continue
            if not process_sale(quantity):          # Bước 2: kiểm tra kho trước
                continue
            final_total = calculate_final_price(quantity, price)   # Bước 3: tính tiền
            complete_sale(quantity, final_total)                   # Bước 4: trừ kho, cộng doanh thu

        elif choice == "3":
            print_report()

        elif choice == "4":
            print("Đã lưu dữ liệu. Cảm ơn bạn đã sử dụng TechStore Management System!")
            break

        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!")


if __name__ == "__main__":
    main()
