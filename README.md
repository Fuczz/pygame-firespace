# Space Shooter

Game bắn tàu vũ trụ nhỏ viết bằng Python và Pygame CE. Giao diện lấy cảm hứng từ ảnh tham khảo: nền tím xám, sao lấp lánh, thiên thạch đa giác và tàu vũ trụ hoạt hình. Game có tiếng súng và tiếng nổ WAV ngắn; các mẫu này được rút gọn từ [mẫu súng CC0](https://sfxmint.com/sounds/impact-gunshot-10) và [mẫu nổ CC0](https://sfxmint.com/sounds/impact-explosion-13). Trang nguồn ghi rõ mẫu âm thanh được tạo bằng AI.

## Chạy trong PyCharm

1. Mở thư mục `space-shooter` bằng PyCharm.
2. Tạo Python Interpreter/virtual environment cho dự án.
3. Mở Terminal trong PyCharm và cài thư viện:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Chạy `main.py` bằng nút Run.

## Điều khiển

- Di chuyển: phím mũi tên hoặc `W`, `A`, `S`, `D`.
- Bắn: giữ chuột trái hoặc phím cách.
- Tạm dừng / tiếp tục: `Esc`.
- Bắt đầu hoặc chơi lại: `Enter`, hoặc dùng các nút trên màn hình.
- Âm thanh nền và hiệu ứng bắn, nổ, thua có thể bật/tắt bằng nút `ÂM THANH`.
- Kỷ lục được lưu ngay khi vượt điểm cao nhất trước đó, không cần đợi hết ván.

## Cơ chế trong game

- Ba loại thiên thạch có kích cỡ lần lượt bằng khoảng một nửa, bằng, và gấp đôi phi thuyền. Chúng cần 1, 2, và 3 phát bắn; điểm nhận được lần lượt là 1, 2, và 3.
- Thiên thạch biến mất khi bay khỏi cạnh dưới màn hình. Khi bị bắn trúng, thanh HP hiện phía trên để cho biết còn bao nhiêu phát bắn cần thiết.
- Boss xuất hiện khi đạt 100, 200, 300 điểm và các mốc 100 điểm tiếp theo. Boss đầu có 50 HP; mỗi boss sau tăng thêm 15 HP, bắn nhanh hơn và tăng cơ hội rơi vật phẩm.
- Sau mỗi boss, thiên thạch xuất hiện thường xuyên hơn và bay nhanh hơn. Boss lượn chậm qua lại, có lõi và động cơ phát sáng, bắn cầu năng lượng lớn, có thể bắn loạt ba quả hoặc thả bom nổ lan.
- Bom gây sát thương cho thiên thạch trong vùng nổ rộng và cho phi thuyền nếu đứng trong vùng đó. Các đợt boss sau có HP cao hơn và tấn công thường xuyên hơn.
- Vật phẩm rơi ngẫu nhiên khi phá thiên thạch hoặc boss: tim thêm một mạng, biểu tượng ba viên đạn, ba mũi tên tăng tốc, hoặc khiên 10 giây. Khiên chặn sát thương từ boss và phá hủy thiên thạch chạm vào tàu.

## Đóng gói thành file `.exe` trên Windows

Trong Terminal của PyCharm, cài PyInstaller rồi đóng gói:

```bash
python -m pip install pyinstaller
python -m PyInstaller --onefile --windowed --name SpaceShooter --add-data "assets;assets" main.py
```

File chạy được sẽ nằm trong thư mục `dist`. Game lưu kỷ lục vào `space_shooter_save.json` trong thư mục làm việc hiện tại; hãy chạy game từ thư mục có quyền ghi để giữ kỷ lục.
