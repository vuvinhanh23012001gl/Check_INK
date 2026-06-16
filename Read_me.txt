
- Module Ket noi Camera
- Module ket noi voi nut nhan 
-  mod

api
- api chon san pham 
- api them/sua/xoa san pham
- api cau hinh 
 - api cau hinh phan mem
 - api san pham  
- huong dan su dung
  + noi luu log
  + huong dan su dung


type = "CaptureProduct"


ErroTimeOutCapture   #Loi chup anh Timeout
Kich thuoc anh  
2048 x 1536
my_pipeline_project/
│
├── stages/                      # 🔥 MỚI: Mỗi giai đoạn là 1 file
│   ├── __init__.py
│   ├── stage_1_ingest.py        # Tầng nhập dữ liệu
│   ├── stage_2_preprocess.py    # Tầng tiền xử lý
│   ├── stage_3_transform.py     # Tầng biến đổi
│   └── stage_4_export.py        # Tầng xuất dữ liệu
│
├── pipeline.py                  # Giờ chỉ còn vài dòng, chỉ dùng để nối các stage

# Có 3 luồng hiện tại luôn bật luồng Conect camera,Luồng check conect COM . nếu con nect thành công sẽ có thêm 2 luồng TX RX của Com nữa



// let dict_lines_of_frames = {
//     "1": {
//         "0": {
//             "calculation_parameters": {
//                 "lineName": "1",
//                 "realityMM": "11",
//                 "captureCount": "111",
//                 "xStart": 441,
//                 "yStart": 139,
//                 "xEnd": 420,
//                 "yEnd": 318,
//                 "coordinateX": 144,
//                 "coordinateY": 31,
//                 "coordinateZ": 30,
//                 "id_item": 6
//             }
//         },
//         "1": {
//             "calculation_parameters": {
//                 "lineName": "1",
//                 "realityMM": "1",
//                 "captureCount": "111",
//                 "xStart": 593,
//                 "yStart": 175,
//                 "xEnd": 569,
//                 "yEnd": 344,
//                 "coordinateX": 67,
//                 "coordinateY": 34,
//                 "coordinateZ": 30,
//                 "id_item": 6
//             }
//         }
//     }
// }
