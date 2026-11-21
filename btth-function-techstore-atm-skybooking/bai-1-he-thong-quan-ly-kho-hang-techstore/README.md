# Bài 1 - Hệ thống quản lý kho hàng & doanh thu (TechStore Inventory)

## Đề bài

Cửa hàng đồ công nghệ cần theo dõi liên tục **số lượng hàng trong kho** và **tổng doanh thu**. Mỗi giao dịch nhập hàng hoặc bán hàng phải cập nhật hai thông số này đồng bộ. Chương trình CLI dùng **biến toàn cục** để lưu trạng thái (`inventory_stock = 100`, `total_revenue = 0.0`) và dùng **hàm có tham số, có giá trị trả về** để tính giá trị đơn hàng.

### Menu

```
========== TECHSTORE MANAGEMENT SYSTEM ==========
1. Nhập thêm hàng vào kho
2. Bán hàng (Tính toán hóa đơn)
3. Xem báo cáo tổng quan
4. Thoát chương trình
=================================================
Chọn chức năng (1-4):
```

### Yêu cầu chức năng

| Chức năng | Hàm | Mô tả |
|---|---|---|
| 1. Nhập hàng | `add_stock(amount)` | Dùng `global` cộng `amount` vào `inventory_stock` |
| 2. Bán hàng | `process_sale(quantity)` → `calculate_final_price(quantity, price)` → `complete_sale(...)` | Kiểm tra kho trước; đủ hàng mới tính tiền: tạm tính = SL × giá, ≥ $1000 giảm 10%, cộng 8% VAT, `return final_total`; sau đó trừ kho, cộng doanh thu |
| 3. Báo cáo | `print_report()` | Có docstring; in tồn kho và tổng doanh thu |
| 4. Thoát | `main()` | Lưu dữ liệu và thoát vòng lặp |

### Edge cases

| Bẫy | Tình huống | Xử lý |
|---|---|---|
| Bẫy 1 | Số lượng hoặc đơn giá ≤ 0 | "Dữ liệu nhập vào phải lớn hơn 0." |
| Bẫy 2 | Nhập chữ vào ô yêu cầu số | Kiểm tra `.isdigit()` trước khi ép kiểu, báo lỗi, không crash |
| (nghiệp vụ) | Mua nhiều hơn tồn kho | "Lỗi: Không đủ hàng trong kho. Tồn kho hiện tại chỉ còn X." |

## (1) Phân tích và thiết kế

### Phân định biến Global / Local

| Biến | Phạm vi | Nằm ở đâu | Giải thích |
|---|---|---|---|
| `inventory_stock` | **Global** | Đầu chương trình | Trạng thái kho dùng chung cho mọi chức năng, tồn tại suốt chương trình |
| `total_revenue` | **Global** | Đầu chương trình | Doanh thu cộng dồn qua nhiều giao dịch |
| `DISCOUNT_THRESHOLD`, `DISCOUNT_RATE`, `VAT_RATE` | Global (hằng số) | Đầu chương trình | Chỉ đọc, không sửa nên không cần `global` |
| `amount` | Local (tham số) | `add_stock` | Số lượng nhập lần này |
| `quantity`, `price` | Local (tham số) | `process_sale`, `calculate_final_price` | Dữ liệu của một đơn hàng |
| `subtotal`, `discount`, `vat`, `final_total` | **Local** | `calculate_final_price` | Chỉ dùng để tính một hóa đơn, mất đi khi hàm kết thúc; `final_total` được `return` ra ngoài |
| `choice`, `new_stock` | Local | `main` | Biến tạm của vòng lặp menu |

- Hàm **sửa** biến toàn cục (`add_stock`, `complete_sale`) phải khai báo `global inventory_stock, total_revenue`.
- Hàm chỉ **đọc** biến toàn cục (`process_sale`, `print_report`) không cần `global`.
- `calculate_final_price` không đụng tới biến toàn cục: nhận dữ liệu qua tham số và trả kết quả bằng `return`, nên tái sử dụng được ở chỗ khác (ví dụ báo giá trước khi bán).

### Luồng xử lý bán hàng (Pseudocode)

```
quantity ← nhập (số nguyên > 0)   ; price ← nhập (số > 0)
NẾU process_sale(quantity) == False: báo không đủ hàng, về menu
final_total ← calculate_final_price(quantity, price)
    subtotal ← quantity × price
    discount ← subtotal × 10% nếu subtotal ≥ 1000, ngược lại 0
    vat ← (subtotal − discount) × 8%
    in hóa đơn; TRẢ VỀ subtotal − discount + vat
complete_sale(quantity, final_total)
    global inventory_stock −= quantity ; global total_revenue += final_total
```

## (2) Triển khai code

File: [`techstore_inventory.py`](techstore_inventory.py)

```python
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
```

## Kết quả

```
Chọn chức năng (1-4): 1
--- NHẬP HÀNG ---
Nhập số lượng sản phẩm muốn thêm: 50
Đã nhập thành công 50 sản phẩm.
Tồn kho hiện tại: 150

Chọn chức năng (1-4): 2
--- BÁN HÀNG ---
Nhập số lượng mua: 10
Nhập đơn giá ($): 150
-> Hóa đơn chi tiết:
Số lượng: 10 | Đơn giá: $150.0
Tạm tính: $1500.0
Giảm giá (10%): $150.0
Thuế VAT (8%): $108.0
Tổng thanh toán: $1458.0
Đã bán thành công!

Chọn chức năng (1-4): 3
--- BÁO CÁO KINH DOANH ---
Tồn kho hiện tại: 140 sản phẩm
Tổng doanh thu: $1458.0

Chọn chức năng (1-4): 2
--- BÁN HÀNG ---
Nhập số lượng mua: 200
Nhập đơn giá ($): 10
Lỗi: Không đủ hàng trong kho. Tồn kho hiện tại chỉ còn 140.

Chọn chức năng (1-4): 2
--- BÁN HÀNG ---
Nhập số lượng mua: 5
Nhập đơn giá ($): 99.5
-> Hóa đơn chi tiết:
Số lượng: 5 | Đơn giá: $99.5
Tạm tính: $497.5
Giảm giá (0%): $0.0
Thuế VAT (8%): $39.8
Tổng thanh toán: $537.3
Đã bán thành công!

Chọn chức năng (1-4): 1
--- NHẬP HÀNG ---
Nhập số lượng sản phẩm muốn thêm: -5
Dữ liệu nhập vào phải lớn hơn 0.

Chọn chức năng (1-4): 1
--- NHẬP HÀNG ---
Nhập số lượng sản phẩm muốn thêm: 0
Dữ liệu nhập vào phải lớn hơn 0.

Chọn chức năng (1-4): 1
--- NHẬP HÀNG ---
Nhập số lượng sản phẩm muốn thêm: abc
Lỗi: Vui lòng nhập số hợp lệ (số lượng là số nguyên)!

Chọn chức năng (1-4): 2
--- BÁN HÀNG ---
Nhập số lượng mua: 10
Nhập đơn giá ($): -3
Dữ liệu nhập vào phải lớn hơn 0.

Chọn chức năng (1-4): 2
--- BÁN HÀNG ---
Nhập số lượng mua: 2.5
Lỗi: Vui lòng nhập số hợp lệ (số lượng là số nguyên)!

Chọn chức năng (1-4): 3
--- BÁO CÁO KINH DOANH ---
Tồn kho hiện tại: 135 sản phẩm
Tổng doanh thu: $1995.3

Chọn chức năng (1-4): 5
Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!

Chọn chức năng (1-4): 4
Đã lưu dữ liệu. Cảm ơn bạn đã sử dụng TechStore Management System!
```

### Bảng kiểm thử

| Kịch bản | Dữ liệu | Kết quả |
|---|---|---|
| Nhập hàng | 50 | Tồn kho 150 (khớp đề) |
| Bán có giảm giá | 10 × $150 | Tạm tính 1500, giảm 150, VAT 108, tổng $1458.0 (khớp đề) |
| Báo cáo | Chọn 3 | Tồn 140, doanh thu $1458.0 (khớp đề) |
| Không đủ hàng | 200 × $10 | Lỗi: Không đủ hàng... chỉ còn 140 |
| Bán không giảm giá | 5 × $99.5 | Tạm tính 497.5 < 1000, VAT 39.8, tổng $537.3 |
| Bẫy 1 | `-5`, `0`, đơn giá `-3` | Dữ liệu nhập vào phải lớn hơn 0. |
| Bẫy 2 | `abc`, số lượng `2.5` | Báo nhập số hợp lệ, không crash |
| Báo cáo cuối | Chọn 3 | Tồn 135, doanh thu $1995.3 |
| Menu sai / thoát | `5`, `4` | Báo lỗi / thoát |

## Ghi chú

- Hóa đơn chi tiết được in trong `calculate_final_price` vì các con số tạm tính, giảm giá, VAT là biến cục bộ của hàm này; hàm vẫn `return final_total` đúng yêu cầu.
- Tiền được làm tròn 2 chữ số (`round(..., 2)`) để tránh sai số dấu phẩy động.
