# BÁO CÁO THỰC NGHIỆM STATIC VS ADAPTIVE CYBER DECEPTION

## 1. Mục tiêu thực nghiệm

Thực nghiệm nhằm đánh giá khả năng của hệ thống AI Agent hỗ trợ Cyber Deception thích ứng dựa trên Honeypot trong việc dẫn dắt hành vi khám phá của đối tượng tấn công mô phỏng.

Câu hỏi nghiên cứu:

**Việc lựa chọn và cập nhật nội dung deception dựa trên hành vi quan sát được có làm tăng số lệnh thực hiện, thời gian tương tác và lượng bằng chứng hành vi thu thập được so với Honeypot tĩnh hay không?**

Ba chỉ số đánh giá chính gồm:

- Số lượng lệnh SSH được Honeypot ghi nhận.
- Thời lượng phiên SSH, tính từ thời điểm bắt đầu đến kết thúc phiên.
- Bằng chứng hành vi bổ sung, đặc biệt là hành vi truy cập tệp mồi nhử.

Đồng thời, thực nghiệm kiểm tra số lượng SSH fingerprint duy nhất nhằm đánh giá khả năng thu thập thêm định danh kỹ thuật.

## 2. Môi trường thực nghiệm

Hệ thống được triển khai trong môi trường mạng máy ảo biệt lập.

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Máy tấn công mô phỏng | Kali Linux | Chạy attacker simulator |
| Honeypot | Cowrie | Mô phỏng SSH và thu thập telemetry |
| AI Agent | Python, Qwen3 1.7B | Phân tích hành vi, lựa chọn deception |
| LLM Runtime | Ollama | Cung cấp mô hình ngôn ngữ |
| Tool API | FastAPI | Cung cấp dữ liệu và thực thi hành động được kiểm soát |
| Data Pipeline | Python | Chuẩn hóa và lưu telemetry |
| Cơ sở dữ liệu | SQLite | Lưu phiên SSH, lệnh và sự kiện |
| Triển khai dịch vụ | Docker Compose, systemd | Vận hành các thành phần |

Máy Kali có địa chỉ `192.168.255.130`, máy Ubuntu chạy Honeypot có địa chỉ `192.168.255.128`. Attacker simulator kết nối qua TCP Gateway tại cổng `2223`.

Đối tượng tấn công được mô phỏng bằng script Python sử dụng thư viện Paramiko. Các tương tác chỉ diễn ra trong môi trường Honeypot kiểm thử.

## 3. Phương pháp thực nghiệm

### 3.1. Nhóm Static Honeypot

Ở chế độ Static:

- Realtime Agent được dừng.
- Artifact `backup_credentials.txt` được khôi phục về nội dung baseline cố định.
- Cowrie tiếp tục ghi nhận các phiên SSH và lệnh thực hiện.
- Nội dung credential không chứa trường `BACKUP_MANIFEST`.

Attacker simulator đọc credential, sau đó khảo sát thư mục backup giả.

### 3.2. Nhóm Adaptive Honeypot

Ở chế độ Adaptive:

- Realtime Agent được bật.
- Artifact ban đầu được khôi phục về cùng baseline với Static.
- Một phiên khởi động (warm-up) tạo dữ liệu hành vi ban đầu.
- Sau khi phiên warm-up kết thúc, Agent phân tích telemetry và lựa chọn cập nhật `backup_credentials`.
- Artifact được bổ sung đường dẫn `BACKUP_MANIFEST=/srv/archive/nightly/manifest.txt`.
- Các phiên đo tiếp theo sử dụng cùng script attacker simulator như nhóm Static.

Khi đọc được trường `BACKUP_MANIFEST`, simulator tiếp tục truy cập file manifest giả. File này chứa các manh mối về cấu hình backup và database giả.

Vì Agent chỉ cập nhật artifact sau khi phiên SSH kết thúc, phiên warm-up không được tính trong nhóm năm phiên đo Adaptive.

### 3.3. Quy trình thu thập dữ liệu

Mỗi chế độ được chạy năm phiên SSH hợp lệ.

Các trường `session_id`, `start_time`, `end_time` và các lệnh được trích xuất từ cơ sở dữ liệu SQLite của Cowrie.

Thời gian phiên SSH được tính theo công thức:

**Session Duration = End Time − Start Time**

Dữ liệu được lưu tại:

`experiments/results/static_vs_adaptive.csv`

Chỉ các phiên SSH đăng nhập thành công và có đầy đủ dữ liệu bắt đầu, kết thúc mới được sử dụng trong bảng đánh giá.

## 4. Kết quả thực nghiệm

### 4.1. Kết quả từng phiên

| Lượt | Static: số lệnh | Static: thời gian SSH (s) | Adaptive: số lệnh | Adaptive: thời gian SSH (s) |
|---|---:|---:|---:|---:|
| 1 | 2 | 0,721 | 3 | 1,108 |
| 2 | 2 | 0,767 | 3 | 0,978 |
| 3 | 2 | 0,854 | 3 | 0,992 |
| 4 | 2 | 0,728 | 3 | 1,037 |
| 5 | 2 | 0,709 | 3 | 0,997 |
| **Trung bình** | **2,0** | **0,756** | **3,0** | **1,022** |

### 4.2. So sánh kết quả tổng hợp

| Tiêu chí | Static | Adaptive |
|---|---:|---:|
| Tổng số phiên | 5 | 5 |
| Số lệnh trung bình mỗi phiên | 2,0 | 3,0 |
| Thời gian SSH trung bình | 0,756 giây | 1,022 giây |
| Số chuỗi lệnh khác nhau | 2 | 3 |
| Tổng số lượt đọc `manifest.txt` | 0 | 5 |
| SSH fingerprint duy nhất | 1 | 1 |

Trong môi trường kiểm thử, số lệnh trung bình ở nhóm Adaptive cao hơn 50% so với nhóm Static. Thời gian phiên SSH trung bình cao hơn khoảng 35,3%, tương đương 0,267 giây.

Nhóm Adaptive ghi nhận năm lượt truy cập manifest, trong khi nhóm Static không ghi nhận lượt truy cập nào.

### 4.3. Đánh giá dữ liệu IOC và hành vi

Hai nhóm đều sử dụng cùng attacker simulator và ghi nhận một SSH fingerprint duy nhất.

Các phiên được thu thập thông qua Cowrie và có dữ liệu về phiên kết nối, thông tin SSH client, sự kiện đăng nhập, lệnh thực hiện và kết thúc phiên.

Nhóm Adaptive thu thập thêm bằng chứng hành vi về việc truy cập file manifest giả. Tuy nhiên, số lượng fingerprint duy nhất không tăng.

Do đó, không thể đồng nhất việc tăng số lệnh hoặc số sự kiện với việc tăng số lượng IOC độc lập.

## 5. Đánh giá kết quả

Thực nghiệm xác nhận chu trình cập nhật deception sau phiên của hệ thống hoạt động thành công.

Khi attacker simulator thực hiện hành vi tìm kiếm credential, Cowrie ghi nhận telemetry. Agent phân tích hành vi, lựa chọn artifact `backup_credentials` và thực hiện cập nhật nội dung thông qua Tool API.

Nội dung artifact được cập nhật sau đó được Cowrie cung cấp trong phiên SSH tiếp theo. Khi phát hiện đường dẫn `BACKUP_MANIFEST`, attacker simulator thực hiện thêm lệnh để đọc file manifest.

Trong phạm vi kịch bản mô phỏng này, việc bổ sung mồi nhử đã làm tăng số lệnh được ghi nhận và thời gian phiên SSH trung bình.

Kết quả cung cấp bằng chứng về khả năng điều chỉnh nội dung deception theo nhóm hành vi được phát hiện và dẫn dắt quy trình khám phá của attacker simulator.

## 6. Giới hạn nghiên cứu

Thực nghiệm tồn tại một số giới hạn:

- **Số lượt thử nghiệm còn nhỏ:** Mỗi chế độ có năm phiên, chưa đủ để đánh giá độ ổn định trong nhiều điều kiện vận hành.
- **Attacker simulator sử dụng quy tắc cố định:** Script được lập trình để đọc manifest khi credential chứa `BACKUP_MANIFEST`. Vì vậy, kết quả chưa đại diện cho quyết định của attacker thực tế.
- **Cập nhật deception sau phiên:** Agent chưa thể điều chỉnh nội dung dựa trên lệnh được thực hiện ngay trong cùng phiên SSH.
- **Thời gian SSH chịu ảnh hưởng của môi trường:** Chênh lệch thời gian có thể chịu tác động từ độ trễ xử lý, kết nối và thời gian thực hiện lệnh bổ sung.
- **Định danh kỹ thuật không tăng:** Cả hai nhóm đều có một SSH fingerprint duy nhất; chưa chứng minh được khả năng thu thập nhiều IOC độc lập hơn.
- **Routing chưa phản ánh nhiều backend độc lập:** Các đường SSH routing trong prototype hiện tại đều dẫn đến cùng môi trường Cowrie.

Vì vậy, kết quả chỉ hỗ trợ kết luận về tác động của mồi nhử thích ứng đối với attacker simulator trong kịch bản đã thiết kế, không chứng minh khả năng giữ chân attacker thật.

## 7. Hướng phát triển

Các hướng phát triển tiếp theo gồm:

1. Xử lý telemetry ngay trong phiên SSH nhằm hỗ trợ cập nhật deception trước khi attacker kết thúc tương tác.
2. Xây dựng nhiều kịch bản attacker simulator với các quy tắc khám phá khác nhau.
3. Thực hiện nhiều lượt đo hơn và kiểm soát các yếu tố ảnh hưởng đến thời gian phiên.
4. Triển khai các backend deception độc lập để đánh giá hiệu quả routing thích ứng.
5. Xây dựng bộ tiêu chí đánh giá IOC và bằng chứng hành vi nhất quán hơn.
6. So sánh các chính sách deception khác nhau thay vì chỉ so sánh sự có mặt của một trường mồi nhử.

## 8. Kết luận

Hệ thống AI Agent hỗ trợ Cyber Deception dựa trên Cowrie đã triển khai và kiểm chứng thành công cơ chế phân tích hành vi, lựa chọn artifact và cập nhật nội dung deception sau phiên SSH.

Trong 10 phiên kiểm thử với attacker simulator, nhóm Adaptive ghi nhận trung bình ba lệnh mỗi phiên so với hai lệnh ở nhóm Static. Thời gian SSH trung bình lần lượt là 1,022 giây và 0,756 giây.

Kết quả cho thấy việc bổ sung mồi nhử có thể dẫn dắt attacker simulator khám phá thêm thông tin giả và tạo ra bằng chứng hành vi bổ sung.

Tuy nhiên, cần các thực nghiệm đa dạng và kiểm soát chặt chẽ hơn trước khi kết luận về hiệu quả giữ chân attacker thực tế hoặc khả năng gia tăng IOC độc lập.
