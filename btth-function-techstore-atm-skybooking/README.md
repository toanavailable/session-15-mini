# Bài tập thực hành Python - Function & Scope: TechStore, Smart ATM, SkyBooking

Tổng hợp 3 bài tập thực hành (BTTH) Session 14 về **Function** và **phạm vi biến (Global / Local)**. Cả 3 bài dùng biến toàn cục để lưu trạng thái hệ thống (tồn kho, số dư, ghế trống, doanh thu), dùng hàm có tham số và `return` để tính toán, khai báo `global` ở những hàm thay đổi trạng thái, và có docstring mô tả tham số và giá trị trả về.

## Thứ tự bài tập

| STT | Bài tập | Kiến thức trọng tâm |
|---|---|---|
| 1 | [Hệ thống quản lý kho hàng & doanh thu (TechStore)](bai-1-he-thong-quan-ly-kho-hang-techstore/) | `global` khi sửa tồn kho / doanh thu; hàm tính giá có biến cục bộ `discount`, `return final_total` |
| 2 | [Hệ thống giao dịch máy ATM (Smart ATM)](bai-2-he-thong-giao-dich-may-atm/) | Hàm trả về trạng thái (`"OK"`, `"ATM_OUT_OF_CASH"`...) để điều hướng; phí là biến cục bộ; khi nào dùng Arguments, khi nào dùng Global |
| 3 | [Hệ thống đặt vé máy bay (SkyBooking)](bai-3-he-thong-dat-ve-may-bay-skybooking/) | Luồng tiền từ hàm tính giá sang hàm đặt vé, hoàn vé, chặn overbooking; vì sao doanh thu phải là biến toàn cục |

Mỗi thư mục bài có mã nguồn Python và `README.md` riêng (đề bài, phân tích Global/Local, pseudocode, mã nguồn, kết quả chạy thử, bảng kiểm thử).

## Cách chạy

Yêu cầu Python 3.x. Vào thư mục bài cần chạy, ví dụ:

```bash
cd bai-1-he-thong-quan-ly-kho-hang-techstore
python techstore_inventory.py
```
