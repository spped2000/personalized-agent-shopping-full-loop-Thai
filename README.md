# Personalized Agent Shopping - Full Loop Thai 🛍️🇹🇭

AI Shopping Agent ที่รองรับภาษาไทยอย่างสมบูรณ์ พัฒนาด้วย Google ADK และ Gemini 2.5 Flash

## ✨ Features

- 🇹🇭 **รองรับภาษาไทยเต็มรูปแบบ** - สามารถสนทนาเป็นภาษาไทยได้อย่างเป็นธรรมชาติ
- 🔍 **ค้นหาอัจฉริยะ** - แปลคำค้นหาภาษาไทยเป็นภาษาอังกฤษอัตโนมัติ
- 📦 **รายละเอียดสินค้าครบถ้วน** - แสดง Description, Features, Reviews
- 💳 **ชำระเงินด้วย QR Code** - แสดง QR Code หลังยืนยันการสั่งซื้อ
- ⚡ **ประสิทธิภาพสูง** - ใช้ข้อมูล 1,000 สินค้า โหลดเร็วภายใน 1 วินาที

## 🚀 Quick Start

### 1. ติดตั้ง Java JDK

Pyserini ต้องการ Java JDK 17 ขึ้นไป

#### Windows 🪟

**วิธีที่ 1: ใช้ Chocolatey (แนะนำ)**
```powershell
# ติดตั้ง Chocolatey ก่อน (ถ้ายังไม่มี)
# https://chocolatey.org/install

choco install openjdk17
```

**วิธีที่ 2: ดาวน์โหลดโดยตรง**
1. ไปที่ https://adoptium.net/
2. เลือก JDK 17 (LTS) สำหรับ Windows
3. ดาวน์โหลดและติดตั้ง
4. เช็คว่า "Set JAVA_HOME" และ "Add to PATH" ถูกเลือก

**ตรวจสอบการติดตั้ง:**
```powershell
java -version
# ควรเห็น: openjdk version "17.x.x"
```

#### macOS 🍎

**วิธีที่ 1: ใช้ Homebrew (แนะนำ)**
```bash
# ติดตั้ง Homebrew ก่อน (ถ้ายังไม่มี)
# https://brew.sh/

brew install openjdk@17

# เพิ่ม Java ไปยัง PATH
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**วิธีที่ 2: ดาวน์โหลดโดยตรง**
1. ไปที่ https://adoptium.net/
2. เลือก JDK 17 (LTS) สำหรับ macOS
3. ดาวน์โหลดและติดตั้ง

**ตรวจสอบการติดตั้ง:**
```bash
java -version
# ควรเห็น: openjdk version "17.x.x"
```

### 2. ติดตั้ง Python Dependencies

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/personalized-agent-shopping-full-loop-Thai.git
cd personalized-agent-shopping-full-loop-Thai

# ติดตั้ง uv (ถ้ายังไม่มี)
# Windows (PowerShell):
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# ติดตั้ง dependencies
uv sync
```

### 3. ดาวน์โหลดข้อมูลสินค้า

ดาวน์โหลดไฟล์ JSON ที่จำเป็นสำหรับ web environment (1,000 สินค้า):

```bash
cd personalized_shopping/shared_libraries/data

# ดาวน์โหลด items_shuffle_1000.json (4.5MB)
uv run python -m gdown https://drive.google.com/uc?id=1EgHdxQ_YxqIQlvvq5iKlCrkEKR6-j0Ib

# ดาวน์โหลด items_ins_v2_1000.json (147KB)
uv run python -m gdown https://drive.google.com/uc?id=1IduG0xl544V_A_jv3tHXC0kyFi7PnyBu

cd ../../..
```

**หมายเหตุ:** ถ้าต้องการข้อมูลเพิ่มเติม (10,000 หรือ 50,000 สินค้า) สามารถดาวน์โหลดได้:

<details>
<summary>คลิกเพื่อดูคำสั่งดาวน์โหลดไฟล์ขนาดใหญ่ (ไม่แนะนำ)</summary>

```bash
cd personalized_shopping/shared_libraries/data

# items_shuffle.json (5.1GB - ทั้งหมด 50,000 สินค้า)
uv run python -m gdown https://drive.google.com/uc?id=1A2whVgOO0euk5O13n2iYDM0bQRkkRduB

# items_ins_v2.json (178MB - attributes สำหรับทั้งหมด)
uv run python -m gdown https://drive.google.com/uc?id=1s2j6NgHljiZzQNL3veZaAiyW98QLDlKR5O

# items_human_ins.json (4.9MB)
uv run python -m gdown https://drive.google.com/uc?id=14Kb5SPBk_jfdLZ_CDBNitW98QLDlKR5O

cd ../../..
```

</details>

### 4. ตั้งค่า Environment Variables

สร้างไฟล์ `.env`:

```bash
GOOGLE_GENAI_API_KEY=your_api_key_here
```

### 5. เตรียมข้อมูลสำหรับ Search Engine

สร้าง document format และ index:

**Windows:**
```powershell
cd personalized_shopping\shared_libraries\search_engine

# สร้างโฟลเดอร์สำหรับเก็บ resources
mkdir resources_100, resources_1k -Force

# แปลงข้อมูล JSON เป็น format ที่ search engine ใช้ได้
uv run python convert_product_file_format.py

# สร้าง search index (ใช้เวลาประมาณ 2-3 วินาที)
uv run python -m pyserini.index.lucene --collection JsonCollection --input resources_1k --index indexes_1k --generator DefaultLuceneDocumentGenerator --threads 1 --storePositions --storeDocvectors --storeRaw

cd ..\..\..
```

**macOS/Linux:**
```bash
cd personalized_shopping/shared_libraries/search_engine

# สร้างโฟลเดอร์สำหรับเก็บ resources
mkdir -p resources_100 resources_1k

# แปลงข้อมูล JSON เป็น format ที่ search engine ใช้ได้
uv run python convert_product_file_format.py

# สร้าง search index (ใช้เวลาประมาณ 2-3 วินาที)
uv run python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input resources_1k \
  --index indexes_1k \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw

cd ../../..
```

### 6. รัน Agent

```bash
uv run adk web
```

เปิดเบราว์เซอร์ไปที่: http://127.0.0.1:8000

## ⚡ Quick Commands (ใช้ uv ทั้งหมด)

```bash
# ติดตั้ง dependencies
uv sync

# รัน agent
uv run adk web

# สร้าง search index
cd personalized_shopping/shared_libraries/search_engine
uv run python -m pyserini.index.lucene --collection JsonCollection --input resources_1k --index indexes_1k --generator DefaultLuceneDocumentGenerator --threads 1 --storePositions --storeDocvectors --storeRaw

# รัน tests (ถ้ามี)
uv run pytest

# Update dependencies
uv sync --upgrade
```

## 💬 ตัวอย่างการใช้งาน

### ภาษาไทย 🇹🇭

```
User: อยากได้ชุดเดรสฤดูร้อน สีฟ้าอ่อน
Agent: ฉันพบชุดเดรสที่น่าสนใจสำหรับคุณค่ะ...

User: อยากทราบข้อมูลเพิ่มเติมตัวที่ถูกที่สุด
Agent: [แสดงรายละเอียดสินค้า + ราคา + สี + ขนาด]

User: ยืนยันการสั่งซื้อ
Agent: [แสดง QR Code สำหรับชำระเงิน] 📱
```

### English 🇺🇸

```
User: I want a summer dress, flowy and floral
Agent: I found some options for you...

User: Tell me more about the cheapest one
Agent: [Shows product details + price + colors + sizes]

User: Confirm purchase
Agent: [Shows QR Code for payment] 📱
```

## 🏗️ Architecture

### Tools
- **search**: ค้นหาสินค้าด้วย Lucene Search Engine
- **click**: นำทางในเว็บไซต์ (คลิกสินค้า, ดูรายละเอียด)
- **show_payment_qr**: แสดง QR Code สำหรับชำระเงิน

### Workflow
1. **Search Phase**: แปลภาษาไทย → อังกฤษ → ค้นหา
2. **Product Exploration**: คลิกดูรายละเอียด (Description, Features, Reviews)
3. **Purchase Confirmation**: เลือก size/color + ยืนยัน
4. **Payment**: แสดง QR Code

## 📊 Performance Optimizations

### ก่อนปรับแต่ง
- ❌ โหลด 5.2GB ข้อมูล (50,000 สินค้า)
- ❌ ใช้เวลานานในการเริ่มต้น
- ❌ ช้าในการค้นหา

### หลังปรับแต่ง
- ✅ โหลด 4.3MB ข้อมูล (1,000 สินค้า)
- ✅ เริ่มต้นภายใน < 1 วินาที
- ✅ ค้นหารวดเร็ว

## 🔧 Configuration

### เพิ่มจำนวนสินค้า

แก้ไข `personalized_shopping/shared_libraries/init_env.py`:

```python
num_product_items = 1000  # เปลี่ยนเป็น 10000 หรือ 50000
```

**หมายเหตุ:** ต้องสร้าง index ใหม่ตามจำนวนสินค้า

### เพิ่มข้อมูลสินค้าไทย

สร้างไฟล์ JSON ใหม่ใน `personalized_shopping/shared_libraries/data/`:

```json
[
  {
    "asin": "TH001",
    "Title": "เสื้อยืดคอกลม ผ้าคอตตอน 100%",
    "Description": "เสื้อยืดคุณภาพดี ใส่สบาย ระบายอากาศได้ดี",
    "BulletPoints": ["ผ้าคอตตอน 100%", "ซักง่าย แห้งเร็ว"],
    "Price": "299.00",
    "options": {
      "size": ["S", "M", "L", "XL"],
      "color": ["ขาว", "ดำ", "เทา"]
    }
  }
]
```

## 🛠️ Tech Stack

- **Google ADK** - Agent Development Kit
- **Gemini 2.5 Flash** - LLM Model
- **Pyserini** - Search Engine (Lucene)
- **WebShop Environment** - E-commerce Simulator
- **Python 3.10+** - Programming Language

## 📝 Key Changes from Original

1. ✅ รองรับภาษาไทยทั้งหมด (input + output)
2. ✅ แปลคำค้นหาอัตโนมัติ (Thai → English)
3. ✅ เพิ่ม QR Code Payment
4. ✅ ปรับปรุงประสิทธิภาพ (1,000 สินค้า แทน 50,000)
5. ✅ แก้ไขปัญหา NumPy compatibility
6. ✅ เพิ่ม mandatory product exploration

## ⚠️ Known Issues

- Description/Features/Reviews บางครั้งอาจไม่มีข้อมูล (ขึ้นกับ dataset)
- ต้องมี Java JDK สำหรับ Pyserini
- NumPy version ต้อง < 2.0 (locked ใน pyproject.toml)

