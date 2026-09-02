"""
Downloader for Authentic Manufacturer Appliance Manuals from Archive.org.
Downloads genuine user/service PDF manuals for:
1. Panasonic Microwave Oven (NN-C994S)
2. Hamilton Beach 4-Slice Toaster (24121)
3. PowerXL Vortex Air Fryer (PXL-VAF)
4. Haier Automatic Drum Washing Machine (HWD-Series)
5. Smeg Built-In Pyrolytic Convection Oven (SFPA6300X)
6. Broan Convertible Kitchen Range Hood / Chimney (QL1)
"""

import io
from pathlib import Path
import httpx
from pypdf import PdfReader

PROJECT_ROOT = Path(__file__).resolve().parent
UPLOAD_DIR = PROJECT_ROOT / "data" / "documents" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

REAL_MANUALS = [
    {
        "appliance": "Microwave Oven",
        "model": "Panasonic NN-C994S",
        "filename": "real_panasonic_nn_c994s_microwave_manual.pdf",
        "url": "https://archive.org/download/Panasonic_NN-C994S_Microwave_Oven_User_Manual/Panasonic_NN-C994S_Microwave_Oven_User_Manual.pdf",
    },
    {
        "appliance": "4-Slice Toaster",
        "model": "Hamilton Beach 24121",
        "filename": "real_hamilton_beach_24121_toaster_manual.pdf",
        "url": "https://archive.org/download/manualsbase-id-642988/642988.pdf",
    },
    {
        "appliance": "Digital Air Fryer",
        "model": "PowerXL Vortex Air Fryer",
        "filename": "real_powerxl_vortex_air_fryer_manual.pdf",
        "url": "https://archive.org/download/pxl-vaf-ib-tp-eng-v-7-201124-web/PXL-VAF_IB_TP_ENG_V7_201124_Web.pdf",
    },
    {
        "appliance": "Drum Washing Machine",
        "model": "Haier Automatic Drum Washer",
        "filename": "real_haier_drum_washing_machine_manual.pdf",
        "url": "https://archive.org/download/manualzilla-id-7282164/7282164.pdf",
    },
    {
        "appliance": "Convection Oven",
        "model": "Smeg SFPA6300X Pyrolytic Oven",
        "filename": "real_smeg_sfpa6300x_oven_manual.pdf",
        "url": "https://archive.org/download/smeg-sfpa-6300-x-60cm-classic-pyrolytic-built-in-oven-user-manual/Smeg_SFPA6300X_60cm_Classic_Pyrolytic_Built_In_Oven_User_Manual.pdf",
    },
    {
        "appliance": "Kitchen Chimney / Hood",
        "model": "Broan QL1 Convertible Range Hood",
        "filename": "real_broan_ql1_range_hood_chimney_manual.pdf",
        "url": "https://archive.org/download/manualsbase-id-465488/465488.pdf",
    },
]

def download_and_verify():
    print("=" * 70)
    print("Downloading 100% Real Manufacturer Appliance Manuals")
    print("=" * 70)

    for item in REAL_MANUALS:
        dest_path = UPLOAD_DIR / item["filename"]
        print(f"\n[*] Downloading {item['appliance']} ({item['model']})...")
        print(f"    Source URL: {item['url']}")

        resp = httpx.get(item["url"], follow_redirects=True, timeout=60.0)
        resp.raise_for_status()

        pdf_bytes = resp.content
        dest_path.write_bytes(pdf_bytes)

        # Verify PDF extraction using pypdf
        reader = PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        sample_snippet = ""
        for page in reader.pages:
            t = page.extract_text() or ""
            if len(t.strip()) > 100:
                sample_snippet = t.strip()[:200].replace("\n", " ")
                break

        print(f"    [OK] Saved to: {dest_path.name}")
        print(f"    [OK] File size: {len(pdf_bytes) / 1024:.1f} KB | Total pages: {page_count}")
        print(f"    [OK] Extracted text preview: \"{sample_snippet}...\"")

    print("\n" + "=" * 70)
    print("All 6 genuine manufacturer appliance manuals downloaded & verified!")
    print("=" * 70)

if __name__ == "__main__":
    download_and_verify()
