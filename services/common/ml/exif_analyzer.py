import piexif
import io
from PIL import Image
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional
import structlog

log = structlog.get_logger()

@dataclass
class EXIFResult:
    capture_date: Optional[date]
    gps_lat: Optional[float]
    gps_lng: Optional[float]
    device_model: Optional[str]
    photo_before_purchase: bool
    days_before_purchase: int
    gps_city_mismatch: bool
    exif_missing: bool

def analyze_exif(image_bytes: bytes, purchase_date: date,
                 delivery_city: str) -> EXIFResult:
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        if "exif" not in image.info:
            return EXIFResult(None, None, None, None, False, 0, False, True)
        
        exif_data = piexif.load(image.info["exif"])
        
        # Extract capture date
        capture_date = None
        date_tag = exif_data.get("Exif", {}).get(piexif.ExifIFD.DateTimeOriginal)
        if date_tag:
            dt_str = date_tag.decode('utf-8', errors='ignore')
            try:
                capture_date = datetime.strptime(dt_str, "%Y:%m:%d %H:%M:%S").date()
            except ValueError:
                pass
        
        # Extract GPS
        gps_lat, gps_lng = None, None
        gps_data = exif_data.get("GPS", {})
        if gps_data:
            gps_lat = _dms_to_decimal(
                gps_data.get(piexif.GPSIFD.GPSLatitude),
                gps_data.get(piexif.GPSIFD.GPSLatitudeRef)
            )
            gps_lng = _dms_to_decimal(
                gps_data.get(piexif.GPSIFD.GPSLongitude),
                gps_data.get(piexif.GPSIFD.GPSLongitudeRef)
            )
        
        # Extract device model
        device_model = None
        model_tag = exif_data.get("0th", {}).get(piexif.ImageIFD.Model)
        if model_tag:
            device_model = model_tag.decode('utf-8', errors='ignore').strip('\x00')
        
        # Key fraud checks
        photo_before_purchase = False
        days_before = 0
        if capture_date and purchase_date:
            if capture_date < purchase_date:
                photo_before_purchase = True
                days_before = (purchase_date - capture_date).days
        
        return EXIFResult(
            capture_date=capture_date,
            gps_lat=gps_lat,
            gps_lng=gps_lng,
            device_model=device_model,
            photo_before_purchase=photo_before_purchase,
            days_before_purchase=days_before,
            gps_city_mismatch=False,  # Implement with geocoding if needed
            exif_missing=False
        )
    
    except Exception as e:
        log.error("EXIF analysis failed", error=str(e))
        return EXIFResult(None, None, None, None, False, 0, False, True)

def _dms_to_decimal(dms, ref) -> Optional[float]:
    if not dms or not ref:
        return None
    try:
        d = dms[0][0] / dms[0][1]
        m = dms[1][0] / dms[1][1]
        s = dms[2][0] / dms[2][1]
        decimal = d + m/60 + s/3600
        ref_str = ref.decode('utf-8') if isinstance(ref, bytes) else ref
        if ref_str in ('S', 'W'):
            decimal = -decimal
        return decimal
    except:
        return None
