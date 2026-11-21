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
