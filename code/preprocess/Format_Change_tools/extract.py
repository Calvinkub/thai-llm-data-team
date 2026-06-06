import gzip
import shutil
import glob

# หาไฟล์ .gz ทั้งหมดในโฟลเดอร์เดียวกัน
gz_files = glob.glob("*.gz")

if not gz_files:
    print("ไม่พบไฟล์ .gz ในโฟลเดอร์นี้")
    exit(0)

for input_path in gz_files:
    # ตัด .gz ออกเป็นชื่อไฟล์ผลลัพธ์
    output_path = input_path[:-3]

    print(f"กำลังแตกไฟล์ {input_path} ...", end=" ")

    try:
        with gzip.open(input_path, "rb") as f_in, open(output_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        print(f"เสร็จสิ้น → {output_path}")
    except Exception as e:
        print(f"ผิดพลาด: {e}")

print(f"\nแตกไฟล์ทั้งหมด {len(gz_files)} ไฟล์")
