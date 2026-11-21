# Bài 2 - Hệ thống giao dịch máy ATM (Smart ATM Machine)

## Đề bài

Phần mềm cho trụ ATM thế hệ mới quản lý cả **số dư tài khoản** người dùng lẫn **lượng tiền mặt vật lý trong máy (ATM Vault)**. Nếu khách rút nhiều hơn số tiền mặt máy đang có thì giao dịch bị từ chối dù tài khoản đủ tiền. Biến toàn cục: `atm_vault_balance = 50000000`, `user_account_balance = 10000000`. Bài yêu cầu tách nghiệp vụ thành hàm, dùng giá trị `return` để quyết định bước tiếp theo và phân biệt rõ Global/Local.

### Menu

```
============= SMART ATM =============
1. Xem số dư
2. Nạp tiền
3. Rút tiền
4. Kết thúc giao dịch
=====================================
Vui lòng chọn giao dịch (1-4):
```

### Yêu cầu chức năng

| Chức năng | Hàm | Mô tả |
|---|---|---|
| 1. Xem số dư | `display_balances()` | In số dư tài khoản và (debug) tiền mặt trong ATM |
| 2. Nạp tiền | `deposit_money(amount)` | `global` tăng cả `user_account_balance` và `atm_vault_balance`; `return True` khi thành công |
| 3. Rút tiền | `check_withdrawal_rules(amount)` → `execute_withdrawal(total_deduction, amount_to_dispense)` | Phí cục bộ `fee = 1100`; trả về trạng thái `INSUFFICIENT_FUNDS` / `ATM_OUT_OF_CASH` / `OK`; OK thì trừ tiền (dùng `global`) và in biên lai |
| 4. Kết thúc | `main()` | "Cảm ơn quý khách đã sử dụng dịch vụ!" |

### Edge cases

| Bẫy | Tình huống | Xử lý |
|---|---|---|
| Bẫy 1 | Số tiền rút không phải bội số 50,000 | "Số tiền rút phải là bội số của 50,000" |
| Bẫy 2 | Nạp/rút số âm, bằng 0 (hoặc nhập chữ) | "Số tiền không hợp lệ" |

## (1) Phân tích và thiết kế

### Khi nào truyền dữ liệu qua Arguments, khi nào dùng Global?

| Hàm | Nhận qua tham số | Đọc Global | Sửa Global (`global`) | Return |
|---|---|---|---|---|
| `display_balances()` | không | Có (cả 2 biến) | Không | `None` |
| `deposit_money(amount)` | `amount` | Có | **Có**: `user_account_balance`, `atm_vault_balance` | `bool` |
| `check_withdrawal_rules(amount)` | `amount` | Có (để so sánh) | Không | `(status, total_deduction)` |
| `execute_withdrawal(total_deduction, amount_to_dispense)` | 2 số tiền đã tính | Có | **Có**: trừ 2 biến | `int` số dư còn lại |
| `read_amount(prompt)` | `prompt` | Không | Không | `int` (0 nếu sai) |

Nguyên tắc áp dụng:
- **Dữ liệu của một giao dịch** (số tiền khách nhập, phí, tổng tiền bị trừ) truyền qua **tham số** và là **biến cục bộ**. Chúng chỉ có ý nghĩa trong một lần giao dịch.
- **Trạng thái của hệ thống** (số dư tài khoản, tiền trong máy) tồn tại xuyên suốt nên là **biến toàn cục**. Chỉ hai hàm thật sự làm thay đổi tiền (`deposit_money`, `execute_withdrawal`) mới khai báo `global`.
- Hàm kiểm tra `check_withdrawal_rules` chỉ đọc và **trả về trạng thái**, không tự sửa tiền. `main()` dựa vào giá trị trả về để in lỗi hoặc gọi `execute_withdrawal`. Nhờ vậy, tiền không bao giờ bị trừ khi giao dịch chưa hợp lệ.

### Luồng rút tiền (Pseudocode)

```
amount ← read_amount(...)
status, total ← check_withdrawal_rules(amount)
    fee ← 1100 (local); total ← amount + fee
    amount ≤ 0             → "INVALID_AMOUNT"
    amount % 50000 ≠ 0     → "NOT_MULTIPLE"
    amount > tiền trong ATM → "ATM_OUT_OF_CASH"
    total > số dư tài khoản → "INSUFFICIENT_FUNDS"
    còn lại                → "OK"
status == "OK" → execute_withdrawal(total, amount)   # global: tài khoản −= total, máy −= amount
ngược lại      → in thông báo lỗi tương ứng
```

## (2) Triển khai code

File: [`smart_atm.py`](smart_atm.py)

```python
"""Smart ATM Machine - Hệ thống giao dịch máy ATM."""

# =====================================================================
# BIẾN TOÀN CỤC (GLOBAL)
# =====================================================================
atm_vault_balance = 50000000        # Tiền mặt có trong ATM (VND)
user_account_balance = 10000000     # Số dư tài khoản người dùng (VND)


def read_amount(prompt):
    """Nhập số tiền từ bàn phím.

    Tham số:
        prompt (str): câu nhắc nhập liệu
    Trả về:
        int: số tiền đã nhập; trả về 0 nếu nhập chữ hoặc số âm
             (0 được các hàm nghiệp vụ coi là số tiền không hợp lệ)
    """
    text = input(prompt).strip()
    if text.isdigit():
        return int(text)
    return 0


def display_balances():
    """In số dư tài khoản người dùng và (debug) lượng tiền mặt trong ATM.

    Tham số: không có (chỉ đọc 2 biến toàn cục).
    Trả về: None.
    """
    print("--- SỐ DƯ TÀI KHOẢN ---")
    print(f"Tài khoản của bạn: {user_account_balance:,} VND")
    print(f"(Debug) Tiền mặt trong ATM: {atm_vault_balance:,} VND")


def deposit_money(amount):
    """Nạp tiền: tăng số dư tài khoản và tăng tiền mặt trong máy.

    Tham số:
        amount (int): số tiền nạp
    Trả về:
        bool: True nếu nạp thành công, False nếu số tiền <= 0
    """
    global user_account_balance, atm_vault_balance
    if amount <= 0:
        return False
    user_account_balance += amount
    atm_vault_balance += amount          # tiền vật lý được đưa vào máy
    return True


def check_withdrawal_rules(amount):
    """Kiểm tra điều kiện rút tiền (chỉ đọc biến toàn cục, không sửa).

    Tham số:
        amount (int): số tiền khách muốn rút
    Trả về:
        tuple (status, total_deduction):
            status (str): "INVALID_AMOUNT", "NOT_MULTIPLE", "ATM_OUT_OF_CASH",
                          "INSUFFICIENT_FUNDS" hoặc "OK"
            total_deduction (int): số tiền thực bị trừ = amount + fee
    """
    fee = 1100                              # biến cục bộ: phí rút tiền
    total_deduction = amount + fee          # biến cục bộ
    if amount <= 0:
        return "INVALID_AMOUNT", total_deduction
    if amount % 50000 != 0:
        return "NOT_MULTIPLE", total_deduction
    if amount > atm_vault_balance:
        return "ATM_OUT_OF_CASH", total_deduction
    if total_deduction > user_account_balance:
        return "INSUFFICIENT_FUNDS", total_deduction
    return "OK", total_deduction


def execute_withdrawal(total_deduction, amount_to_dispense):
    """Thực hiện rút tiền và in biên lai.

    Tham số:
        total_deduction (int): số tiền trừ khỏi tài khoản (gồm phí)
        amount_to_dispense (int): số tiền mặt máy nhả ra cho khách
    Trả về:
        int: số dư tài khoản còn lại
    """
    global user_account_balance, atm_vault_balance
    user_account_balance -= total_deduction
    atm_vault_balance -= amount_to_dispense
    print("Giao dịch đang xử lý...")
    print(f"Phí giao dịch: {total_deduction - amount_to_dispense:,} VND")
    print(f"Bạn đã rút thành công {amount_to_dispense:,} VND.")
    print(f"Số dư tài khoản còn lại: {user_account_balance:,} VND.")
    return user_account_balance


def main():
    """Vòng lặp menu ATM, điều hướng theo giá trị return của các hàm nghiệp vụ."""
    while True:
        print("\n============= SMART ATM =============")
        print("1. Xem số dư")
        print("2. Nạp tiền")
        print("3. Rút tiền")
        print("4. Kết thúc giao dịch")
        print("=" * 37)
        choice = input("Vui lòng chọn giao dịch (1-4): ").strip()

        if choice == "1":
            display_balances()

        elif choice == "2":
            print("--- NẠP TIỀN ---")
            amount = read_amount("Nhập số tiền muốn nạp: ")
            if deposit_money(amount):
                print(f"Giao dịch thành công! Số dư tài khoản hiện tại: {user_account_balance:,} VND.")
            else:
                print("Số tiền không hợp lệ")                                   # Bẫy 2

        elif choice == "3":
            print("--- RÚT TIỀN ---")
            amount = read_amount("Nhập số tiền cần rút: ")
            status, total_deduction = check_withdrawal_rules(amount)
            if status == "OK":
                execute_withdrawal(total_deduction, amount)
            elif status == "INVALID_AMOUNT":
                print("Số tiền không hợp lệ")                                   # Bẫy 2
            elif status == "NOT_MULTIPLE":
                print("Số tiền rút phải là bội số của 50,000")                  # Bẫy 1
            elif status == "ATM_OUT_OF_CASH":
                print("Giao dịch thất bại: Máy ATM không đủ tiền mặt để phục vụ.")
            else:   # INSUFFICIENT_FUNDS
                print(f"Giao dịch thất bại: Số dư tài khoản không đủ "
                      f"(cần {total_deduction:,} VND bao gồm phí).")

        elif choice == "4":
            print("Cảm ơn quý khách đã sử dụng dịch vụ!")
            break

        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!")


if __name__ == "__main__":
    main()
```

## Kết quả

```
Vui lòng chọn giao dịch (1-4): 1
--- SỐ DƯ TÀI KHOẢN ---
Tài khoản của bạn: 10,000,000 VND
(Debug) Tiền mặt trong ATM: 50,000,000 VND

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 5000000
Giao dịch đang xử lý...
Phí giao dịch: 1,100 VND
Bạn đã rút thành công 5,000,000 VND.
Số dư tài khoản còn lại: 4,998,900 VND.

Vui lòng chọn giao dịch (1-4): 2
--- NẠP TIỀN ---
Nhập số tiền muốn nạp: 2000000
Giao dịch thành công! Số dư tài khoản hiện tại: 6,998,900 VND.

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 60000000
Giao dịch thất bại: Máy ATM không đủ tiền mặt để phục vụ.

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 120000
Số tiền rút phải là bội số của 50,000

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: -500000
Số tiền không hợp lệ

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 0
Số tiền không hợp lệ

Vui lòng chọn giao dịch (1-4): 2
--- NẠP TIỀN ---
Nhập số tiền muốn nạp: -100
Số tiền không hợp lệ

Vui lòng chọn giao dịch (1-4): 2
--- NẠP TIỀN ---
Nhập số tiền muốn nạp: abc
Số tiền không hợp lệ

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 11000000
Giao dịch thất bại: Số dư tài khoản không đủ (cần 11,001,100 VND bao gồm phí).

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 6998900
Số tiền rút phải là bội số của 50,000

Vui lòng chọn giao dịch (1-4): 3
--- RÚT TIỀN ---
Nhập số tiền cần rút: 6950000
Giao dịch đang xử lý...
Phí giao dịch: 1,100 VND
Bạn đã rút thành công 6,950,000 VND.
Số dư tài khoản còn lại: 47,800 VND.

Vui lòng chọn giao dịch (1-4): 1
--- SỐ DƯ TÀI KHOẢN ---
Tài khoản của bạn: 47,800 VND
(Debug) Tiền mặt trong ATM: 40,050,000 VND

Vui lòng chọn giao dịch (1-4): x
Lựa chọn không hợp lệ, vui lòng chọn từ 1 đến 4!

Vui lòng chọn giao dịch (1-4): 4
Cảm ơn quý khách đã sử dụng dịch vụ!
```

### Bảng kiểm thử

| Kịch bản | Dữ liệu | Kết quả |
|---|---|---|
| Xem số dư | Chọn 1 | 10,000,000 / ATM 50,000,000 (khớp đề) |
| Rút hợp lệ | 5,000,000 | Phí 1,100; còn 4,998,900 VND (khớp đề) |
| Nạp tiền | 2,000,000 | Giao dịch thành công, số dư 6,998,900 VND |
| ATM hết tiền | 60,000,000 | Máy ATM không đủ tiền mặt để phục vụ (khớp đề) |
| Bẫy 1 | 120,000; 6,998,900 | Số tiền rút phải là bội số của 50,000 |
| Bẫy 2 | rút `-500000`, `0`; nạp `-100`, `abc` | Số tiền không hợp lệ |
| Không đủ số dư | 11,000,000 | Thất bại, cần 11,001,100 VND gồm phí |
| Rút gần hết | 6,950,000 | Còn 47,800 VND; ATM còn 40,050,000 |
| Menu sai / thoát | `x`, `4` | Báo lỗi / Cảm ơn quý khách... |

## Ghi chú

- **Thứ tự kiểm tra:** đề liệt kê `INSUFFICIENT_FUNDS` trước, nhưng output mẫu rút 60,000,000 (vượt cả số dư 10 triệu lẫn tiền trong máy) lại in "Máy ATM không đủ tiền mặt". Vì vậy chương trình kiểm tra `ATM_OUT_OF_CASH` trước để khớp output mẫu.
- `check_withdrawal_rules` trả về tuple `(status, total_deduction)` để `main()` có sẵn tổng tiền bị trừ (gồm phí cục bộ) khi gọi `execute_withdrawal(total_deduction, amount_to_dispense)`.
- Thêm 2 trạng thái `INVALID_AMOUNT` và `NOT_MULTIPLE` để xử lý Bẫy 1 và 2 ngay trong hàm kiểm tra, đúng yêu cầu "hàm kiểm tra trả về lỗi".
- Ví dụ trong đề là các tình huống độc lập (rút 5 triệu từ số dư 10 triệu, nạp 2 triệu vào số dư 10 triệu). Trong phiên chạy liên tục ở trên, chương trình rút trước rồi mới nạp nên số dư sau khi nạp là 6,998,900.
