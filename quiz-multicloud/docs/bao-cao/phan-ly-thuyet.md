# CHƯƠNG 1. BỐI CẢNH VÀ LÝ DO LỰA CHỌN ỨNG DỤNG

## 1.1. Bối cảnh

Chuyển đổi số trong giáo dục đang là xu hướng tất yếu tại Việt Nam và trên thế giới. Sau giai đoạn dịch COVID-19, phần lớn các trường đại học, trung học và trung tâm đào tạo đã làm quen với việc dạy học trực tuyến. Trong đó, hoạt động kiểm tra, đánh giá vẫn là khâu tốn nhiều công sức nhất: giáo viên phải soạn đề, in đề, coi thi, chấm bài, tổng hợp điểm và lập báo cáo. Với các bài kiểm tra trắc nghiệm, phần lớn khâu chấm điểm có tính lặp lại cao và hoàn toàn có thể tự động hóa.

Bên cạnh đó, nhu cầu cấp **chứng nhận điện tử** sau khi hoàn thành một khóa học hoặc bài thi ngày càng phổ biến (các nền tảng như Coursera, Microsoft Learn, AWS Skill Builder đều cấp chứng nhận dạng PDF hoặc huy hiệu số). Chứng nhận điện tử giúp người học lưu trữ, chia sẻ dễ dàng và giúp đơn vị đào tạo tiết kiệm chi phí in ấn.

Các công cụ sẵn có như Google Forms hay Microsoft Forms đáp ứng tốt nhu cầu khảo sát đơn giản, nhưng còn hạn chế khi cần: phân quyền rõ ràng giữa giáo viên và học sinh, kiểm soát mỗi học sinh chỉ làm bài một lần, tự động sinh chứng nhận có mã định danh riêng, và thống kê chi tiết theo từng câu hỏi. Đây là khoảng trống mà một hệ thống chuyên biệt có thể lấp đầy.

## 1.2. Bài toán đặt ra

Nhóm đặt ra bài toán xây dựng **QuizCloud – hệ thống tạo form khảo sát và thi trắc nghiệm trực tuyến** với các yêu cầu sau:

**Yêu cầu chức năng:**

- Quản lý người dùng với hai vai trò tách biệt: Giáo viên và Học sinh; đăng nhập an toàn qua nhà cung cấp danh tính chuyên nghiệp.
- Giáo viên: tạo bài thi (thời gian làm bài, ngưỡng điểm đạt), thêm câu hỏi một đáp án hoặc nhiều đáp án, nhập câu hỏi hàng loạt từ file CSV, mở/đóng bài thi.
- Học sinh: xem danh sách bài thi đang mở, làm bài có đồng hồ đếm ngược, tự động nộp khi hết giờ, mỗi bài chỉ được nộp một lần.
- Hệ thống tự động chấm điểm ngay sau khi nộp, hiển thị kết quả chi tiết từng câu.
- Tự động sinh file **chứng nhận PDF** (nếu đạt) hoặc **phiếu kết quả PDF** (nếu chưa đạt), lưu trữ an toàn và cung cấp đường dẫn tải có thời hạn; gửi email thông báo kết quả.
- Giáo viên xem thống kê (điểm trung bình, cao nhất, thấp nhất, tỉ lệ đạt, tỉ lệ trả lời đúng từng câu), xuất bảng điểm CSV và báo cáo HTML.

**Yêu cầu phi chức năng:**

- Bảo mật: chỉ giáo viên tạo đề mới xem được đáp án và kết quả của bài thi đó; học sinh chỉ xem được bài làm của chính mình; file chứng nhận không được công khai.
- Khả năng mở rộng: khâu chấm điểm và sinh PDF phải chịu được lượng bài nộp tăng đột biến (ví dụ cả lớp nộp bài cùng lúc khi hết giờ).
- Chi phí thấp: tận dụng tối đa các gói miễn phí, chỉ trả tiền theo mức sử dụng thực tế.
- Dễ bảo trì: tách biệt rõ phần quản lý dữ liệu/người dùng và phần xử lý tính toán.

## 1.3. Lý do lựa chọn ứng dụng

Nhóm lựa chọn ứng dụng thi trắc nghiệm trực tuyến vì các lý do sau:

1. **Tính thực tiễn cao:** ứng dụng giải quyết một nhu cầu có thật, gần gũi với chính môi trường học tập của sinh viên; có thể dùng ngay cho các bài kiểm tra nhanh trên lớp.
2. **Thể hiện rõ giá trị của điện toán đám mây:** tải của hệ thống không đều – gần như không có truy cập ngoài giờ thi, nhưng tăng vọt trong vài phút cuối mỗi bài thi. Đây là trường hợp điển hình mà mô hình serverless và trả tiền theo mức dùng (pay-as-you-go) phát huy hiệu quả, thay vì phải duy trì máy chủ chạy 24/7.
3. **Có nhiều thành phần khác nhau phù hợp để phân bổ lên nhiều đám mây:** quản lý danh tính, cơ sở dữ liệu quan hệ, xử lý tính toán theo sự kiện, lưu trữ file, gửi email. Mỗi thành phần có thể đặt trên nền tảng mạnh nhất về mảng đó.
4. **Có nhiều chức năng để trình diễn:** phân quyền, tính điểm tự động, sinh file động (PDF/HTML/CSV), thống kê – đáp ứng yêu cầu "càng nhiều chức năng càng nhiều điểm" của đề bài.
5. **Khả thi trong thời gian thực hiện:** phạm vi vừa đủ để nhóm hoàn thành, kiểm thử và triển khai trong khoảng 3 tuần với chi phí gần như bằng 0.

## 1.4. Lý do lựa chọn tổ hợp AWS + Microsoft Azure

Trong các tổ hợp được đề xuất, nhóm lựa chọn **AWS + Microsoft Azure** – hai nhà cung cấp đám mây công cộng lớn nhất thế giới hiện nay. Mỗi nền tảng được giao phần việc phù hợp với thế mạnh của nó:

| Thành phần | Đặt tại | Lý do |
|---|---|---|
| Quản lý danh tính, phân quyền Giáo viên/Học sinh | Azure (Microsoft Entra External ID) | Microsoft có kinh nghiệm lâu năm về quản lý danh tính doanh nghiệp (Active Directory); các trường học thường đã dùng Microsoft 365 nên dễ tích hợp; miễn phí cho 50.000 người dùng hoạt động hàng tháng đầu tiên. |
| Cơ sở dữ liệu câu hỏi, bài làm, điểm số | Azure (Azure SQL Database) | Dữ liệu có cấu trúc quan hệ rõ ràng (bài thi – câu hỏi – bài nộp – người dùng); Azure SQL là SQL Server được quản lý hoàn toàn, có gói miễn phí không giới hạn thời gian. |
| Ứng dụng web | Azure (App Service) | Nằm cùng nền tảng với Entra ID và Azure SQL, giảm độ trễ và đơn giản hóa cấu hình mạng; có gói F1 miễn phí. |
| Chấm điểm, sinh PDF | AWS (Lambda + API Gateway) | AWS Lambda là dịch vụ serverless ra đời sớm và phổ biến nhất; tự động co giãn theo số bài nộp; nằm trong nhóm dịch vụ miễn phí vĩnh viễn với 1 triệu request mỗi tháng. |
| Lưu trữ chứng nhận, link tải có thời hạn | AWS (Amazon S3) | S3 là dịch vụ lưu trữ đối tượng tiêu chuẩn của ngành, hỗ trợ sẵn presigned URL để cấp quyền tải tạm thời mà không cần công khai bucket. |
| Gửi email kết quả, giám sát | AWS (SES, CloudWatch) | Tích hợp sẵn với Lambda, chi phí rất thấp. |

Ngoài lý do kỹ thuật, kiến trúc đa đám mây còn giúp hệ thống **tránh phụ thuộc vào một nhà cung cấp duy nhất** (vendor lock-in): thành phần chấm điểm giao tiếp với ứng dụng web qua một API HTTP đơn giản, nên có thể chuyển sang Azure Functions hoặc nền tảng khác mà không cần sửa phần còn lại. Đồng thời, tổ hợp này giúp các thành viên trong nhóm được làm quen với cả hai nền tảng phổ biến nhất trên thị trường tuyển dụng.

## 1.5. Phạm vi và giới hạn

- Hệ thống tập trung vào câu hỏi trắc nghiệm (một hoặc nhiều đáp án); chưa hỗ trợ câu hỏi tự luận.
- Chống gian lận ở mức cơ bản (mỗi học sinh nộp một lần, giới hạn thời gian); chưa có giám sát webcam hay khóa trình duyệt.
- Triển khai ở quy mô demo, sử dụng các gói miễn phí; chưa đánh giá hiệu năng với hàng nghìn người dùng đồng thời.

# CHƯƠNG 2. TÌM HIỂU CÁC CHỨC NĂNG VÀ DỊCH VỤ CỦA AWS VÀ AZURE

## 2.1. Tổng quan về điện toán đám mây

Theo định nghĩa của Viện Tiêu chuẩn và Công nghệ Quốc gia Hoa Kỳ (NIST SP 800-145), điện toán đám mây là mô hình cho phép truy cập qua mạng một cách thuận tiện, theo nhu cầu, tới một tập hợp tài nguyên tính toán dùng chung có thể cấu hình (mạng, máy chủ, lưu trữ, ứng dụng, dịch vụ), được cấp phát và giải phóng nhanh chóng với nỗ lực quản lý tối thiểu. NIST nêu ra 5 đặc điểm cốt lõi:

- **Tự phục vụ theo nhu cầu (on-demand self-service):** người dùng tự tạo tài nguyên mà không cần liên hệ nhà cung cấp.
- **Truy cập mạng rộng rãi (broad network access):** truy cập qua Internet từ nhiều loại thiết bị.
- **Gộp tài nguyên (resource pooling):** tài nguyên vật lý được chia sẻ cho nhiều khách hàng.
- **Co giãn nhanh (rapid elasticity):** tăng/giảm tài nguyên nhanh chóng theo tải.
- **Dịch vụ đo lường được (measured service):** tính phí theo mức sử dụng thực tế.

**Các mô hình dịch vụ:**

| Mô hình | Nhà cung cấp quản lý | Người dùng quản lý | Ví dụ AWS | Ví dụ Azure |
|---|---|---|---|---|
| IaaS – Hạ tầng như dịch vụ | Phần cứng, mạng, ảo hóa | Hệ điều hành, runtime, ứng dụng, dữ liệu | Amazon EC2 | Azure Virtual Machines |
| PaaS – Nền tảng như dịch vụ | Thêm hệ điều hành, runtime | Ứng dụng, dữ liệu | AWS Elastic Beanstalk | Azure App Service |
| FaaS / Serverless | Toàn bộ hạ tầng, tự co giãn | Chỉ mã nguồn hàm | AWS Lambda | Azure Functions |
| SaaS – Phần mềm như dịch vụ | Toàn bộ | Chỉ sử dụng | Amazon WorkMail | Microsoft 365 |

**Các mô hình triển khai:** đám mây công cộng (public cloud), đám mây riêng (private cloud), đám mây lai (hybrid cloud – kết hợp hạ tầng tại chỗ với đám mây công cộng) và **đa đám mây (multi-cloud)** – sử dụng đồng thời dịch vụ của nhiều nhà cung cấp đám mây công cộng. Hệ thống QuizCloud thuộc mô hình đa đám mây.

## 2.2. Amazon Web Services (AWS)

### 2.2.1. Giới thiệu

Amazon Web Services là nền tảng điện toán đám mây của tập đoàn Amazon, chính thức cung cấp dịch vụ từ năm 2006 với Amazon S3 (lưu trữ) và Amazon EC2 (máy chủ ảo). AWS là nhà cung cấp tiên phong của mô hình đám mây công cộng hiện đại và hiện cung cấp hơn 200 dịch vụ. Theo các báo cáo thị trường của Synergy Research Group, AWS liên tục giữ vị trí dẫn đầu thị phần hạ tầng đám mây toàn cầu trong nhiều năm.

### 2.2.2. Hạ tầng toàn cầu

- **Region (vùng):** một khu vực địa lý độc lập (ví dụ `ap-southeast-1` – Singapore), gồm nhiều Availability Zone. Dữ liệu không tự rời khỏi Region nếu người dùng không cấu hình.
- **Availability Zone (AZ):** một hoặc nhiều trung tâm dữ liệu có nguồn điện, làm mát và mạng độc lập, kết nối với nhau bằng đường truyền tốc độ cao, độ trễ thấp. Triển khai trên nhiều AZ giúp ứng dụng chịu được sự cố của một trung tâm dữ liệu.
- **Edge Location / Point of Presence:** các điểm phân phối nội dung của Amazon CloudFront và Route 53, đặt gần người dùng cuối để giảm độ trễ.

### 2.2.3. Các nhóm dịch vụ chính

| Nhóm | Dịch vụ tiêu biểu | Chức năng |
|---|---|---|
| Tính toán | Amazon EC2 | Máy chủ ảo, nhiều cấu hình CPU/RAM/GPU |
| | AWS Lambda | Chạy mã theo sự kiện, không cần quản lý máy chủ, tính phí theo số request và thời gian chạy |
| | Amazon ECS, EKS, AWS Fargate | Chạy container (Docker, Kubernetes) |
| | AWS Elastic Beanstalk | PaaS triển khai ứng dụng web |
| Lưu trữ | Amazon S3 | Lưu trữ đối tượng, độ bền thiết kế 99,999999999% (11 số 9) |
| | Amazon EBS, Amazon EFS | Ổ đĩa khối cho EC2; hệ thống file chia sẻ |
| | S3 Glacier | Lưu trữ lưu trữ dài hạn giá rẻ |
| Cơ sở dữ liệu | Amazon RDS, Amazon Aurora | CSDL quan hệ được quản lý (MySQL, PostgreSQL, SQL Server…) |
| | Amazon DynamoDB | CSDL NoSQL key-value, độ trễ mili giây |
| Mạng | Amazon VPC | Mạng riêng ảo |
| | Amazon API Gateway | Tạo, công bố và bảo vệ API REST/HTTP/WebSocket |
| | Amazon CloudFront, Route 53 | Mạng phân phối nội dung (CDN); DNS |
| | Elastic Load Balancing | Cân bằng tải |
| Bảo mật & danh tính | AWS IAM | Quản lý người dùng, vai trò, chính sách phân quyền |
| | Amazon Cognito | Đăng nhập cho người dùng cuối của ứng dụng |
| | AWS KMS, Secrets Manager | Quản lý khóa mã hóa; lưu trữ bí mật |
| | AWS WAF, AWS Shield | Tường lửa ứng dụng web; chống DDoS |
| Tích hợp ứng dụng | Amazon SQS, Amazon SNS | Hàng đợi thông điệp; thông báo publish/subscribe |
| | Amazon EventBridge, AWS Step Functions | Bus sự kiện; điều phối luồng công việc |
| | Amazon SES | Gửi email giao dịch, email hàng loạt |
| Giám sát & quản trị | Amazon CloudWatch | Thu thập log, số liệu, cảnh báo |
| | AWS CloudTrail | Ghi lại lịch sử gọi API để kiểm toán |
| | AWS CloudFormation | Hạ tầng dưới dạng mã (Infrastructure as Code) |
| | AWS Budgets, Cost Explorer | Quản lý và cảnh báo chi phí |
| Trí tuệ nhân tạo | Amazon Bedrock, Amazon SageMaker | Mô hình nền tảng (generative AI); xây dựng, huấn luyện mô hình học máy |
| | Amazon Rekognition, Amazon Textract | Phân tích ảnh/video; trích xuất văn bản từ tài liệu |

### 2.2.4. Các dịch vụ AWS sử dụng trong QuizCloud

- **AWS Lambda:** chứa mã Python chấm điểm và sinh PDF. Mỗi lần học sinh nộp bài, Lambda được gọi một lần; khi nhiều học sinh nộp cùng lúc, AWS tự động chạy nhiều bản song song. Giới hạn đáng chú ý: thời gian chạy tối đa 15 phút mỗi lần gọi, bộ nhớ cấu hình từ 128 MB đến 10.240 MB.
- **Amazon API Gateway (HTTP API):** cung cấp địa chỉ HTTPS công khai để ứng dụng web trên Azure gọi tới Lambda.
- **Amazon S3:** lưu file PDF trong bucket riêng tư (bật *Block Public Access*). Người dùng tải file qua **presigned URL** – đường dẫn có chữ ký số và thời hạn (tối đa 7 ngày với chữ ký Signature Version 4), hết hạn thì không dùng được nữa.
- **Amazon SES:** gửi email thông báo kết quả kèm link tải chứng nhận. Ở chế độ sandbox, SES chỉ gửi tới địa chỉ đã xác minh, đủ cho mục đích demo.
- **AWS IAM:** cấp cho Lambda một vai trò (role) chỉ có quyền ghi/đọc thư mục `certificates/` trong đúng một bucket và quyền gửi email – tuân thủ nguyên tắc đặc quyền tối thiểu.
- **Amazon CloudWatch:** lưu log mỗi lần chấm điểm, phục vụ theo dõi và gỡ lỗi.

## 2.3. Microsoft Azure

### 2.3.1. Giới thiệu

Microsoft Azure là nền tảng điện toán đám mây của Microsoft, được công bố năm 2008 với tên gọi Windows Azure, chính thức cung cấp thương mại từ năm 2010 và đổi tên thành Microsoft Azure vào năm 2014. Azure là nhà cung cấp hạ tầng đám mây lớn thứ hai thế giới theo thị phần, với thế mạnh đặc biệt trong khối doanh nghiệp, cơ quan nhà nước và giáo dục nhờ hệ sinh thái Windows Server, SQL Server, Microsoft 365 và Active Directory.

### 2.3.2. Hạ tầng toàn cầu

- **Geography:** khu vực địa lý (thường tương ứng một quốc gia hoặc thị trường) đảm bảo yêu cầu về nơi lưu trữ dữ liệu và tuân thủ pháp lý.
- **Region:** tập hợp trung tâm dữ liệu trong một khu vực (ví dụ *Southeast Asia* – Singapore, *East Asia* – Hồng Kông). Azure là một trong những nhà cung cấp có số lượng Region lớn nhất.
- **Availability Zone:** các trung tâm dữ liệu độc lập về vật lý trong cùng Region, tương tự khái niệm AZ của AWS.
- **Region pair:** nhiều Region được ghép cặp với một Region khác trong cùng Geography để phục vụ sao lưu và khôi phục thảm họa; khi cập nhật hệ thống, Microsoft không cập nhật cả hai Region trong cặp cùng lúc.

### 2.3.3. Các nhóm dịch vụ chính

| Nhóm | Dịch vụ tiêu biểu | Chức năng |
|---|---|---|
| Tính toán | Azure Virtual Machines | Máy chủ ảo Windows/Linux |
| | Azure App Service | PaaS triển khai web app, API (Python, .NET, Node.js, Java, PHP) |
| | Azure Functions | Serverless theo sự kiện |
| | Azure Kubernetes Service, Azure Container Apps | Chạy container |
| Lưu trữ | Azure Blob Storage | Lưu trữ đối tượng, hỗ trợ SAS token để cấp quyền tạm thời |
| | Azure Files, Azure Disk Storage | Chia sẻ file SMB/NFS; ổ đĩa cho VM |
| Cơ sở dữ liệu | Azure SQL Database | SQL Server được quản lý hoàn toàn (PaaS) |
| | Azure Cosmos DB | CSDL NoSQL phân tán toàn cầu, nhiều mô hình dữ liệu |
| | Azure Database for PostgreSQL / MySQL | CSDL mã nguồn mở được quản lý |
| Mạng | Azure Virtual Network | Mạng riêng ảo |
| | Azure Front Door, Azure CDN | Phân phối nội dung, cân bằng tải toàn cầu |
| | Azure API Management, Application Gateway | Quản lý API; cân bằng tải lớp 7 có WAF |
| Danh tính | Microsoft Entra ID (trước đây là Azure Active Directory) | Quản lý danh tính và truy cập cho nhân viên/tổ chức, đăng nhập một lần (SSO), xác thực đa yếu tố |
| | Microsoft Entra External ID | Quản lý danh tính cho khách hàng/người dùng bên ngoài của ứng dụng (thế hệ kế tiếp của Azure AD B2C) |
| Bảo mật | Azure Key Vault | Lưu trữ khóa, bí mật, chứng chỉ |
| | Microsoft Defender for Cloud | Đánh giá và bảo vệ an ninh tài nguyên đám mây |
| Giám sát & quản trị | Azure Monitor, Application Insights | Thu thập log, số liệu; giám sát hiệu năng ứng dụng |
| | Azure Resource Manager, Bicep | Quản lý tài nguyên; hạ tầng dưới dạng mã |
| | Microsoft Cost Management | Theo dõi và cảnh báo chi phí |
| Trí tuệ nhân tạo | Azure OpenAI Service, Azure AI Foundry | Mô hình ngôn ngữ lớn, xây dựng ứng dụng AI |
| | Azure AI Services | Thị giác máy tính, giọng nói, dịch thuật, Document Intelligence |
| DevOps | Azure DevOps, tích hợp GitHub Actions | Quản lý mã nguồn, CI/CD |

### 2.3.4. Các dịch vụ Azure sử dụng trong QuizCloud

- **Microsoft Entra External ID:** đăng ký, đăng nhập cho giáo viên và học sinh. Ứng dụng định nghĩa hai **App Role** là `Teacher` và `Student`; quản trị viên gán vai trò cho từng tài khoản, vai trò được trả về trong ID token (giao thức OpenID Connect) để ứng dụng phân quyền. Microsoft công bố mức miễn phí cho 50.000 người dùng hoạt động hằng tháng đầu tiên. Lưu ý: từ ngày 01/05/2025, Azure AD B2C không còn bán cho khách hàng mới, nên nhóm sử dụng Entra External ID.
- **Azure SQL Database:** lưu bảng người dùng, bài thi, câu hỏi, bài nộp và điểm. Nhóm sử dụng **gói miễn phí (free offer)**: mỗi subscription được tạo tối đa 10 database serverless, mỗi database được miễn phí 100.000 vCore-giây tính toán, 32 GB dữ liệu và 32 GB sao lưu mỗi tháng, không giới hạn thời gian. Database serverless tự tạm dừng khi không có truy cập để tiết kiệm tài nguyên.
- **Azure App Service (gói F1 Free):** chạy ứng dụng web Python (Flask). Gói F1 giới hạn 60 phút CPU mỗi ngày và không hỗ trợ chế độ *Always On*, phù hợp cho môi trường demo.

## 2.4. Đối chiếu dịch vụ tương đương giữa AWS và Azure

| Nhu cầu | AWS | Azure |
|---|---|---|
| Máy chủ ảo | Amazon EC2 | Azure Virtual Machines |
| Serverless | AWS Lambda | Azure Functions |
| PaaS web | AWS Elastic Beanstalk, AWS App Runner | Azure App Service |
| Kubernetes | Amazon EKS | Azure Kubernetes Service |
| Lưu trữ đối tượng | Amazon S3 | Azure Blob Storage |
| Link truy cập tạm thời | S3 Presigned URL | Blob SAS token |
| CSDL quan hệ | Amazon RDS, Aurora | Azure SQL Database, Azure Database for PostgreSQL/MySQL |
| CSDL NoSQL | Amazon DynamoDB | Azure Cosmos DB |
| Danh tính người dùng cuối | Amazon Cognito | Microsoft Entra External ID |
| Phân quyền quản trị | AWS IAM | Azure RBAC + Microsoft Entra ID |
| Quản lý API | Amazon API Gateway | Azure API Management |
| Hàng đợi | Amazon SQS | Azure Queue Storage, Azure Service Bus |
| Giám sát | Amazon CloudWatch | Azure Monitor |
| Hạ tầng dưới dạng mã | AWS CloudFormation | ARM template, Bicep |
| Lưu trữ bí mật | AWS Secrets Manager | Azure Key Vault |
| AI tạo sinh | Amazon Bedrock | Azure OpenAI Service |

# CHƯƠNG 3. MÔ HÌNH HOẠT ĐỘNG CỦA AWS VÀ AZURE

## 3.1. Các nguyên tắc chung

### 3.1.1. Mô hình trách nhiệm chia sẻ (Shared Responsibility Model)

Cả AWS và Azure đều áp dụng mô hình trách nhiệm chia sẻ về bảo mật. Nhà cung cấp chịu trách nhiệm bảo mật **của** đám mây (an ninh vật lý trung tâm dữ liệu, phần cứng, mạng lõi, lớp ảo hóa), còn khách hàng chịu trách nhiệm bảo mật **trong** đám mây (dữ liệu, tài khoản, phân quyền, cấu hình). Phạm vi trách nhiệm của khách hàng giảm dần từ IaaS đến PaaS, serverless và SaaS. Ví dụ trong QuizCloud: Microsoft chịu trách nhiệm vá lỗi hệ điều hành của App Service và engine SQL Server, AWS chịu trách nhiệm môi trường chạy Lambda; nhóm chịu trách nhiệm cấu hình bucket S3 không công khai, giữ bí mật khóa kết nối và phân quyền đúng vai trò.

### 3.1.2. Mô hình tính phí

Cả hai nền tảng đều tính phí theo mức sử dụng (pay-as-you-go), không cần đầu tư trước, đồng thời có các hình thức giảm giá:

| Hình thức | AWS | Azure |
|---|---|---|
| Trả theo mức dùng | On-Demand | Pay-as-you-go |
| Cam kết dài hạn (1–3 năm) | Reserved Instances, Savings Plans | Reserved Instances, Azure Savings Plan |
| Tài nguyên dư thừa giá rẻ | Spot Instances | Spot Virtual Machines |
| Gói miễn phí cho người mới | Từ 15/07/2025: tài khoản *Free plan* nhận 100 USD credit, có thể nhận thêm tối đa 100 USD khi khám phá dịch vụ, dùng trong 6 tháng | Azure free account; **Azure for Students**: 100 USD credit, không cần thẻ tín dụng |
| Dịch vụ miễn phí vĩnh viễn (trong hạn mức) | Ví dụ Lambda: 1 triệu request và 400.000 GB-giây mỗi tháng | Ví dụ Azure SQL Database free offer, App Service F1 |

### 3.1.3. Phương thức truy cập và quản trị

Cả hai nền tảng đều cho phép quản trị qua giao diện web (AWS Management Console, Azure Portal), dòng lệnh (AWS CLI; Azure CLI, Azure PowerShell), bộ thư viện lập trình (AWS SDK – ví dụ boto3 cho Python; Azure SDK) và hạ tầng dưới dạng mã (CloudFormation; ARM/Bicep). Mọi thao tác cuối cùng đều được chuyển thành lời gọi API tới nền tảng, nhờ đó có thể tự động hóa hoàn toàn.

## 3.2. Mô hình hoạt động của AWS

### 3.2.1. Tổ chức tài khoản và tài nguyên

- **AWS Account** là đơn vị cơ bản: chứa tài nguyên, là ranh giới bảo mật và là đơn vị tính phí. Tài khoản gốc (root user) có toàn quyền và chỉ nên dùng cho các tác vụ đặc biệt.
- **AWS Organizations** cho phép gom nhiều tài khoản thành một tổ chức, quản lý tập trung chính sách (Service Control Policies) và hóa đơn hợp nhất.
- Mỗi tài nguyên được định danh duy nhất bằng **ARN** (Amazon Resource Name), ví dụ `arn:aws:s3:::quizcloud-certs/certificates/*`.
- Phần lớn dịch vụ hoạt động theo **Region**: tài nguyên tạo ở Region nào thì nằm ở Region đó (một số dịch vụ như IAM, Route 53, CloudFront là toàn cầu).

### 3.2.2. Mô hình phân quyền IAM

AWS IAM hoạt động theo mô hình: **chủ thể** (IAM user, IAM role, dịch vụ AWS) thực hiện **hành động** (ví dụ `s3:PutObject`) trên **tài nguyên** (ARN) và được cho phép hoặc từ chối bởi các **chính sách** (policy) dạng JSON. Mặc định mọi yêu cầu đều bị từ chối; một lệnh từ chối tường minh (explicit deny) luôn được ưu tiên hơn lệnh cho phép. Dịch vụ như Lambda nhận quyền thông qua **IAM role** với thông tin xác thực tạm thời do AWS tự cấp và tự xoay vòng, nên mã nguồn không cần chứa khóa truy cập.

### 3.2.3. Mô hình hoạt động của AWS Lambda

1. Nhà phát triển tải lên gói mã (file zip hoặc container image) và cấu hình hàm xử lý (handler), bộ nhớ, thời gian chờ, biến môi trường.
2. Khi có sự kiện (yêu cầu HTTP qua API Gateway, file mới trên S3, thông điệp SQS…), Lambda khởi tạo một môi trường thực thi biệt lập (nếu chưa có sẵn – gọi là *cold start*) rồi gọi hàm với dữ liệu sự kiện.
3. Môi trường thực thi có thể được giữ lại và tái sử dụng cho các lần gọi tiếp theo (*warm start*), nhờ đó các đối tượng như kết nối SDK được khởi tạo một lần.
4. Khi nhiều sự kiện đến cùng lúc, Lambda tạo thêm môi trường để xử lý song song (concurrency) mà không cần cấu hình máy chủ.
5. Phí tính theo số lần gọi và thời gian chạy nhân với dung lượng bộ nhớ (GB-giây).

## 3.3. Mô hình hoạt động của Azure

### 3.3.1. Phân cấp quản lý tài nguyên

Azure tổ chức tài nguyên theo bốn cấp:

1. **Microsoft Entra tenant:** đại diện cho một tổ chức, chứa danh tính người dùng, nhóm và ứng dụng.
2. **Management group:** nhóm nhiều subscription để áp dụng chính sách chung.
3. **Subscription:** đơn vị tính phí và giới hạn hạn mức tài nguyên (ví dụ subscription *Azure for Students*).
4. **Resource group:** thùng chứa logic gom các tài nguyên có cùng vòng đời (ví dụ toàn bộ tài nguyên của QuizCloud đặt trong `rg-quizcloud`; khi kết thúc chỉ cần xóa resource group là xóa hết).
5. **Resource:** từng tài nguyên cụ thể (web app, SQL database…).

Mọi yêu cầu tạo, sửa, xóa tài nguyên đều đi qua **Azure Resource Manager (ARM)** – lớp quản lý thống nhất, xác thực yêu cầu qua Entra ID và kiểm tra quyền trước khi chuyển tới dịch vụ tương ứng.

### 3.3.2. Mô hình phân quyền

Azure tách biệt hai loại phân quyền:

- **Azure RBAC** (Role-Based Access Control): kiểm soát ai được quản trị tài nguyên nào. Một phép gán vai trò gồm: chủ thể (người dùng, nhóm, managed identity) + định nghĩa vai trò (Owner, Contributor, Reader hoặc vai trò tùy chỉnh) + phạm vi (management group, subscription, resource group hoặc resource). Quyền được kế thừa từ phạm vi cha xuống phạm vi con.
- **Phân quyền trong ứng dụng** qua Entra ID: ứng dụng đăng ký (app registration) định nghĩa App Role, quản trị viên gán vai trò cho người dùng, vai trò được đưa vào token. QuizCloud dùng cơ chế này để phân biệt Giáo viên/Học sinh.

### 3.3.3. Mô hình hoạt động của Microsoft Entra External ID (luồng OpenID Connect)

1. Người dùng bấm "Đăng nhập" trên QuizCloud; ứng dụng chuyển hướng trình duyệt tới trang đăng nhập của Entra External ID kèm mã định danh ứng dụng và địa chỉ callback.
2. Người dùng đăng ký hoặc đăng nhập (email và mật khẩu, có thể bật xác thực đa yếu tố) theo *user flow* đã cấu hình.
3. Entra chuyển hướng về địa chỉ callback kèm mã ủy quyền (authorization code).
4. Máy chủ QuizCloud dùng mã này cùng client secret để đổi lấy **ID token** (định dạng JWT) chứa thông tin người dùng và danh sách vai trò.
5. QuizCloud kiểm tra token, đọc vai trò `Teacher` hoặc `Student`, tạo phiên làm việc. Người dùng chưa được gán vai trò sẽ bị từ chối truy cập.

### 3.3.4. Mô hình hoạt động của Azure App Service và Azure SQL Database

**App Service** chạy ứng dụng trên một **App Service plan** – tập tài nguyên tính toán (CPU, RAM) do Azure quản lý. Nhà phát triển chỉ cần đẩy mã nguồn; Azure tự cài thư viện, chạy ứng dụng sau một reverse proxy, cung cấp tên miền `*.azurewebsites.net` có sẵn HTTPS. Có thể tăng cấu hình (scale up) hoặc tăng số bản chạy (scale out) khi đổi sang gói trả phí.

**Azure SQL Database** chế độ serverless tự động điều chỉnh năng lực tính toán theo tải trong khoảng vCore tối thiểu–tối đa đã cấu hình và tự **tạm dừng** sau một khoảng thời gian không có kết nối; lần kết nối đầu tiên sau khi tạm dừng sẽ mất vài giây để khởi động lại. Azure tự động sao lưu, vá lỗi và đảm bảo tính sẵn sàng cao.

## 3.4. Mô hình hoạt động của hệ thống QuizCloud trên hai đám mây

*[Gợi ý chèn Hình: Sơ đồ kiến trúc tổng thể QuizCloud – lấy từ README]*

Luồng xử lý chính khi học sinh làm bài:

1. Học sinh truy cập ứng dụng web trên **Azure App Service**, đăng nhập qua **Entra External ID** và nhận vai trò `Student`.
2. Học sinh chọn bài thi; dữ liệu đề được đọc từ **Azure SQL Database**.
3. Khi nộp bài, ứng dụng web lưu bài làm vào Azure SQL Database (trạng thái "đang chấm"), sau đó gửi yêu cầu HTTPS gồm đáp án của học sinh và đáp án đúng tới **Amazon API Gateway**, kèm khóa bí mật dùng chung trong header để xác thực.
4. API Gateway chuyển yêu cầu tới **AWS Lambda**. Lambda chấm điểm, sinh file PDF, ghi vào **Amazon S3**, tạo **presigned URL**, gửi email qua **Amazon SES** và ghi log vào **CloudWatch**.
5. Lambda trả kết quả (điểm, chi tiết từng câu, mã chứng nhận, đường dẫn file) về ứng dụng web; ứng dụng cập nhật điểm vào Azure SQL Database và hiển thị cho học sinh.
6. Mỗi lần học sinh hoặc giáo viên mở lại trang kết quả, ứng dụng xin một presigned URL mới, vì URL cũ đã hết hạn.

**Các quyết định thiết kế quan trọng:**

- **Lambda không kết nối trực tiếp tới Azure SQL Database.** Nếu làm vậy, phải cài trình điều khiển ODBC cho SQL Server trong môi trường Lambda và mở tường lửa của Azure SQL cho dải IP không cố định của Lambda. Thay vào đó, ứng dụng web gửi đủ dữ liệu cần chấm, Lambda chỉ tính toán và trả kết quả – thành phần trên AWS trở thành *stateless* (không lưu trạng thái), dễ thay thế và dễ kiểm thử.
- **Ranh giới giữa hai đám mây là một API HTTP duy nhất** với hai thao tác: `grade` (chấm điểm) và `presign` (lấy link tải mới). Hợp đồng dữ liệu đơn giản giúp hai thành viên phụ trách hai nền tảng làm việc song song.
- **Dữ liệu cá nhân tối thiểu đi qua AWS:** chỉ tên, email học sinh (để in chứng nhận và gửi email), tên bài thi và đáp án.
- **Xử lý lỗi:** nếu lời gọi sang AWS thất bại, bài làm vẫn được lưu trên Azure với trạng thái "lỗi chấm" và có thể chấm lại sau.

# CHƯƠNG 4. PHÂN TÍCH, ĐÁNH GIÁ ƯU KHUYẾT ĐIỂM CỦA AWS VÀ AZURE

## 4.1. Amazon Web Services

**Ưu điểm:**

- **Hệ sinh thái dịch vụ rộng và trưởng thành nhất:** hơn 200 dịch vụ, nhiều dịch vụ ra đời sớm nhất trong phân khúc (S3, EC2, Lambda), được kiểm chứng ở quy mô rất lớn.
- **Thị phần dẫn đầu, cộng đồng lớn:** tài liệu, khóa học, ví dụ mã nguồn và câu trả lời trên các diễn đàn rất phong phú; chứng chỉ AWS có giá trị cao trên thị trường tuyển dụng.
- **Serverless mạnh:** Lambda tích hợp sẵn với hầu hết dịch vụ khác của AWS (API Gateway, S3, SQS, EventBridge…), hạn mức miễn phí vĩnh viễn rộng rãi.
- **Phân quyền chi tiết:** IAM cho phép giới hạn quyền tới từng hành động trên từng tài nguyên cụ thể.
- **Hạ tầng toàn cầu rộng**, độ tin cậy cao, nhiều tùy chọn cấu hình phần cứng.

**Nhược điểm:**

- **Độ phức tạp cao với người mới:** số lượng dịch vụ và tùy chọn quá lớn; IAM policy, VPC, cách tính phí có đường cong học tập dốc.
- **Cách tính phí phức tạp, khó dự đoán:** mỗi dịch vụ có nhiều thành phần phí (request, dung lượng, băng thông ra Internet…); dễ phát sinh chi phí ngoài ý muốn nếu quên xóa tài nguyên (ví dụ NAT Gateway, EC2, RDS).
- **Giao diện Console thiếu nhất quán** giữa các dịch vụ.
- **Tích hợp với hệ sinh thái Microsoft** (Active Directory, Microsoft 365) không liền mạch bằng Azure.
- Chưa có Region đặt tại Việt Nam; người dùng trong nước thường dùng Region Singapore.

## 4.2. Microsoft Azure

**Ưu điểm:**

- **Mạnh về danh tính và doanh nghiệp:** Microsoft Entra ID là nền tảng danh tính được nhiều tổ chức sử dụng; tích hợp liền mạch với Microsoft 365, Teams, Windows. Rất phù hợp cho môi trường trường học vốn đã dùng tài khoản Microsoft.
- **Đám mây lai (hybrid) tốt:** Azure Arc, Azure Stack giúp kết nối hạ tầng tại chỗ với đám mây; có lợi thế bản quyền cho khách hàng đã dùng Windows Server và SQL Server.
- **PaaS thân thiện với nhà phát triển:** App Service triển khai ứng dụng nhanh; tích hợp chặt với Visual Studio, VS Code và GitHub (cùng thuộc Microsoft).
- **Ưu đãi cho sinh viên:** Azure for Students cấp 100 USD credit không cần thẻ tín dụng; Azure SQL Database có gói miễn phí không giới hạn thời gian.
- **Quản lý tài nguyên trực quan:** mô hình Resource Group giúp gom và xóa tài nguyên theo dự án dễ dàng; AI tạo sinh mạnh nhờ quan hệ đối tác với OpenAI.

**Nhược điểm:**

- **Đổi tên và thay đổi sản phẩm thường xuyên:** ví dụ Azure Active Directory đổi thành Microsoft Entra ID, Azure AD B2C ngừng bán cho khách hàng mới và được thay bằng Entra External ID – tài liệu cũ dễ gây nhầm lẫn.
- **Cổng quản trị và tài liệu đôi khi phức tạp,** nhiều dịch vụ chồng chéo chức năng (ví dụ nhiều lựa chọn cho hàng đợi, nhiều lựa chọn cho cân bằng tải).
- **Gói miễn phí có giới hạn chặt:** App Service F1 chỉ có 60 phút CPU mỗi ngày, không có Always On; database serverless tự tạm dừng nên lần truy cập đầu chậm.
- **Cộng đồng mã nguồn mở và tài liệu cho Linux/Python** từng ít hơn AWS, dù đã cải thiện nhiều.
- Tương tự AWS, chưa có Region đặt tại Việt Nam.

## 4.3. So sánh tổng hợp

| Tiêu chí | AWS | Azure |
|---|---|---|
| Năm ra mắt thương mại | 2006 | 2010 |
| Vị trí thị phần hạ tầng đám mây | Thứ nhất | Thứ hai |
| Số lượng dịch vụ | Hơn 200 | Hơn 200 |
| Thế mạnh nổi bật | Serverless, lưu trữ, độ phủ dịch vụ, cộng đồng | Danh tính, doanh nghiệp, hybrid cloud, hệ sinh thái Microsoft |
| Quản lý danh tính người dùng cuối | Amazon Cognito | Microsoft Entra External ID |
| Tổ chức tài nguyên | Account, Region, tag | Tenant, Subscription, Resource Group |
| Ưu đãi sinh viên | Free plan credit (6 tháng), AWS Educate | Azure for Students (100 USD, không cần thẻ) |
| Độ khó với người mới | Cao | Trung bình – cao |
| Vai trò trong QuizCloud | Xử lý: chấm điểm, sinh và lưu PDF, gửi email | Quản lý: người dùng, phân quyền, dữ liệu, giao diện web |

## 4.4. Đánh giá kiến trúc đa đám mây AWS + Azure trong QuizCloud

**Ưu điểm:**

- Tận dụng thế mạnh riêng của từng nền tảng: Azure cho danh tính và dữ liệu quan hệ, AWS cho xử lý serverless và lưu trữ file.
- Giảm phụ thuộc vào một nhà cung cấp; thành phần chấm điểm có thể thay thế độc lập.
- Cô lập sự cố: nếu dịch vụ chấm điểm trên AWS gặp lỗi, người dùng vẫn đăng nhập, xem đề và nộp bài bình thường; bài làm được lưu lại để chấm sau.
- Tối ưu chi phí: kết hợp các gói miễn phí của cả hai nền tảng, chi phí vận hành ở quy mô demo gần như bằng 0.

**Nhược điểm và cách khắc phục:**

| Nhược điểm | Cách khắc phục trong QuizCloud |
|---|---|
| Phức tạp hơn khi phải quản trị hai nền tảng, hai hệ thống phân quyền, hai hóa đơn | Ranh giới giữa hai đám mây chỉ là một API; mỗi thành viên phụ trách một nền tảng; bật Budget Alert trên cả hai |
| Độ trễ mạng khi gọi qua Internet giữa hai đám mây | Chọn Region gần nhau (Azure Southeast Asia và AWS ap-southeast-1 đều ở Singapore); mỗi lần nộp bài chỉ gọi một lần |
| Phí truyền dữ liệu ra Internet (egress) | Dữ liệu gửi qua lại chỉ vài KB; file PDF được tải thẳng từ S3 về trình duyệt, không đi qua Azure |
| Bảo mật kênh giao tiếp giữa hai đám mây | Dùng HTTPS và khóa bí mật dùng chung trong header, so sánh theo thời gian hằng định; có thể nâng cấp lên chữ ký HMAC hoặc OAuth client credentials |
| Quản lý bí mật phân tán | Lưu bí mật trong cấu hình môi trường của App Service và Lambda, không đưa vào mã nguồn; có thể chuyển sang Azure Key Vault/AWS Secrets Manager |

## 4.5. Kết luận chương

AWS và Azure đều là các nền tảng trưởng thành, có danh mục dịch vụ tương đương nhau ở hầu hết các nhóm chức năng. Sự khác biệt nằm ở thế mạnh và hệ sinh thái: AWS nổi bật về độ phủ dịch vụ, serverless và cộng đồng; Azure nổi bật về quản lý danh tính, tích hợp doanh nghiệp và ưu đãi cho giáo dục. Việc phân chia QuizCloud thành phần "quản lý" trên Azure và phần "xử lý" trên AWS giúp hệ thống tận dụng được ưu điểm của cả hai, đồng thời các nhược điểm cố hữu của kiến trúc đa đám mây được giảm thiểu nhờ thiết kế ranh giới đơn giản và dữ liệu trao đổi tối thiểu.

# TÀI LIỆU THAM KHẢO

1. P. Mell, T. Grance, *The NIST Definition of Cloud Computing*, NIST Special Publication 800-145, 2011.
2. Amazon Web Services, *Overview of Amazon Web Services* (AWS Whitepaper), https://docs.aws.amazon.com/whitepapers/latest/aws-overview/
3. Amazon Web Services, *AWS Global Infrastructure*, https://aws.amazon.com/about-aws/global-infrastructure/
4. Amazon Web Services, *AWS Free Tier*, https://aws.amazon.com/free/ (thông báo thay đổi ngày 16/07/2025).
5. Amazon Web Services, *AWS Lambda Developer Guide*, https://docs.aws.amazon.com/lambda/
6. Amazon Web Services, *Amazon S3 User Guide – Sharing objects with presigned URLs*, https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html
7. Amazon Web Services, *Shared Responsibility Model*, https://aws.amazon.com/compliance/shared-responsibility-model/
8. Microsoft, *Azure documentation*, https://learn.microsoft.com/azure/
9. Microsoft, *Azure SQL Database free offer*, https://learn.microsoft.com/azure/azure-sql/database/free-tier
10. Microsoft, *Microsoft Entra External ID overview*, https://learn.microsoft.com/entra/external-id/
11. Microsoft, *Azure App Service plans overview*, https://learn.microsoft.com/azure/app-service/overview-hosting-plans
12. Microsoft, *Shared responsibility in the cloud*, https://learn.microsoft.com/azure/security/fundamentals/shared-responsibility
13. Synergy Research Group, các báo cáo thị phần thị trường hạ tầng đám mây, https://www.srgresearch.com/
