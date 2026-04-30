import { useState, useRef, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Upload, AlertCircle, CheckCircle, Camera, FileText, ChevronDown, Loader2 } from 'lucide-react'

function CameraCapture({ onCapture, onRetake, image }) {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const ipImgRef = useRef(null)
  const [devices, setDevices] = useState([])
  const [selectedDevice, setSelectedDevice] = useState('')
  const [useIpCam, setUseIpCam] = useState(false)
  const [ipCamUrl, setIpCamUrl] = useState('http://100.89.91.92:8080/video')

  useEffect(() => {
    // Enumerate cameras
    navigator.mediaDevices.enumerateDevices().then(deviceInfos => {
      const videoDevices = deviceInfos.filter(d => d.kind === 'videoinput')
      setDevices(videoDevices)
      if (videoDevices.length > 0) {
        // Prefer a back/environment camera if available, otherwise pick the first one
        const backCamera = videoDevices.find(d => d.label.toLowerCase().includes('back'))
        setSelectedDevice(backCamera ? backCamera.deviceId : videoDevices[0].deviceId)
      }
    })
  }, [])

  const startCamera = async (deviceId) => {
    try {
      // Stop existing tracks before switching
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop())
      }
      
      const constraints = deviceId 
        ? { video: { deviceId: { exact: deviceId } } }
        : { video: { facingMode: 'environment' } }
        
      const stream = await navigator.mediaDevices.getUserMedia(constraints)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (err) {
      console.error("Camera error:", err)
      alert("Please allow camera access to process your return. File uploads are strictly not allowed.")
    }
  }

  useEffect(() => {
    if (!image && selectedDevice) {
      startCamera(selectedDevice)
    }
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop())
      }
    }
  }, [image, selectedDevice])

  const handleCapture = () => {
    // 1. Get GPS Location
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = { lat: pos.coords.latitude, lon: pos.coords.longitude }
        performCapture(loc)
      },
      (err) => {
        console.warn("Location denied or failed", err)
        performCapture(null)
      }
    )
  }

  const performCapture = (location) => {
    if (useIpCam && ipImgRef.current) {
      // In a real scenario we'd draw to canvas, but IP cam images often have CORS blocked.
      // So we will trigger a fetch to the /shot.jpg endpoint instead of canvas.toDataURL.
      const shotUrl = ipCamUrl.replace('/video', '/shot.jpg')
      fetch(shotUrl)
        .then(res => res.blob())
        .then(blob => {
          const reader = new FileReader()
          reader.onloadend = () => onCapture(reader.result, location)
          reader.readAsDataURL(blob)
        })
        .catch(err => {
          console.error("IP Cam capture failed (CORS?)", err)
          alert("Failed to capture from IP Camera. Check CORS or use file upload.")
        })
    } else if (videoRef.current && canvasRef.current) {
      const video = videoRef.current
      const canvas = canvasRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      canvas.getContext('2d').drawImage(video, 0, 0)
      const base64 = canvas.toDataURL('image/jpeg', 0.8)
      
      video.srcObject.getTracks().forEach(track => track.stop())
      onCapture(base64, location)
    }
  }

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      navigator.geolocation.getCurrentPosition(
        pos => processFile(file, { lat: pos.coords.latitude, lon: pos.coords.longitude }),
        () => processFile(file, null)
      )
    }
  }

  const processFile = (file, location) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop())
      }
      onCapture(reader.result, location)
    }
    reader.readAsDataURL(file)
  }

  return (
    <div style={{ marginBottom: 20 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 8 }}>
        <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: '#ccc' }}>
          Item Photo (Live Capture Only) <span style={{ color: '#00D4AA' }}>*</span>
        </label>
        
        {!image && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <label style={{ color: '#888', fontSize: 11, display: 'flex', alignItems: 'center', gap: 4 }}>
              <input type="checkbox" checked={useIpCam} onChange={e => setUseIpCam(e.target.checked)} />
              IP Camera
            </label>
            {!useIpCam && devices.length > 1 && (
              <select 
                value={selectedDevice} 
                onChange={(e) => setSelectedDevice(e.target.value)}
                style={{ 
                  background: 'rgba(255,255,255,0.05)', color: '#fff', border: '1px solid rgba(255,255,255,0.1)',
                  padding: '4px 8px', borderRadius: 6, fontSize: 11, outline: 'none', maxWidth: 160
                }}
              >
                {devices.map((d, i) => (
                  <option key={d.deviceId} value={d.deviceId} style={{ color: '#000' }}>
                    {d.label || `Camera ${i + 1}`}
                  </option>
                ))}
              </select>
            )}
          </div>
        )}
      </div>

      {!image && useIpCam && (
        <div style={{ marginBottom: 12 }}>
          <input 
            type="text" 
            value={ipCamUrl}
            onChange={e => setIpCamUrl(e.target.value)}
            placeholder="http://100.89.91.92:8080/video"
            style={{ width: '100%', padding: '8px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 6, color: '#fff', fontSize: 12 }}
          />
        </div>
      )}

      <div style={{ 
        background: '#0A0E1A', borderRadius: 12, overflow: 'hidden', 
        border: '1px solid rgba(255,255,255,0.1)', position: 'relative',
        minHeight: 240, display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        {image ? (
          <div style={{ width: '100%', position: 'relative' }}>
            <img src={image} style={{ width: '100%', display: 'block' }} alt="Captured item" />
            <button type="button" onClick={onRetake} style={{
              position: 'absolute', bottom: 16, right: 16, padding: '8px 16px',
              background: 'rgba(0,0,0,0.6)', border: '1px solid #fff', 
              borderRadius: 8, color: '#fff', fontSize: 12, cursor: 'pointer'
            }}>Retake Photo</button>
          </div>
        ) : useIpCam ? (
          <div style={{ width: '100%', position: 'relative' }}>
            <img ref={ipImgRef} src={ipCamUrl} style={{ width: '100%', display: 'block', maxHeight: 400, objectFit: 'cover' }} crossOrigin="anonymous" alt="IP Cam Feed" />
            <button type="button" onClick={handleCapture} style={{
              position: 'absolute', bottom: 24, left: '50%', transform: 'translateX(-50%)',
              width: 56, height: 56, borderRadius: '50%', background: '#00D4AA',
              border: '4px solid #fff', boxShadow: '0 0 10px rgba(0,0,0,0.5)', cursor: 'pointer'
            }} />
          </div>
        ) : (
          <div style={{ width: '100%', position: 'relative' }}>
            <video ref={videoRef} autoPlay playsInline style={{ width: '100%', display: 'block', maxHeight: 400, objectFit: 'cover' }} />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
            <button type="button" onClick={handleCapture} style={{
              position: 'absolute', bottom: 24, left: '50%', transform: 'translateX(-50%)',
              width: 56, height: 56, borderRadius: '50%', background: '#00D4AA',
              border: '4px solid #fff', boxShadow: '0 0 10px rgba(0,0,0,0.5)', cursor: 'pointer'
            }} />
          </div>
        )}
      </div>
      

    </div>
  )
}

const CLAIM_TYPES = [
  { value: 'INR',            label: '📦 Item Not Received',      desc: 'Package never arrived' },
  { value: 'DAMAGE',         label: '💔 Item Damaged',           desc: 'Product arrived broken or damaged' },
  { value: 'WRONG_ITEM',     label: '🔄 Wrong Item Received',    desc: 'Received a different product' },
  { value: 'QUALITY_ISSUE',  label: '⚠️ Quality Issue',          desc: 'Does not match description' },
  { value: 'CHANGE_OF_MIND', label: '🔁 Change of Mind',         desc: 'No longer needed' },
]

function FormField({ label, children, required, hint }) {
  return (
    <div style={{ marginBottom: 20 }}>
      <label style={{ display: 'block', fontSize: 13, fontWeight: 500, color: '#ccc', marginBottom: 8 }}>
        {label} {required && <span style={{ color: '#00D4AA' }}>*</span>}
      </label>
      {children}
      {hint && <div style={{ fontSize: 11, color: '#555', marginTop: 5 }}>{hint}</div>}
    </div>
  )
}

function SuccessScreen({ claimId }) {
  return (
    <div style={{
      textAlign: 'center', padding: '48px 32px', maxWidth: 480,
      animation: 'fadeUp 0.4s ease forwards',
    }}>
      <div style={{
        width: 80, height: 80, borderRadius: '50%', margin: '0 auto 28px',
        background: 'rgba(0,255,136,0.1)', border: '1px solid rgba(0,255,136,0.3)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        boxShadow: '0 0 40px rgba(0,255,136,0.2)',
      }}>
        <CheckCircle size={38} color="#00FF88" />
      </div>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12, color: '#fff' }}>
        Return Request Received ✓
      </h1>
      <p style={{ color: '#888', fontSize: 15, lineHeight: 1.6, marginBottom: 8 }}>
        Your refund will be processed in <strong style={{ color: '#ccc' }}>3–5 business days</strong>.
        We'll send you an email update.
      </p>
      <p style={{ fontSize: 12, color: '#444', marginBottom: 32, fontFamily: 'Space Mono, monospace' }}>
        Ref: {claimId || 'CLM-' + Date.now().toString(36).toUpperCase()}
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        <a href="/track" style={{
          padding: '13px 0', borderRadius: 12, textAlign: 'center',
          background: 'rgba(0,212,170,0.1)', border: '1px solid rgba(0,212,170,0.3)',
          color: '#00D4AA', fontSize: 13, fontWeight: 600, display: 'block',
        }}>
          Track My Return →
        </a>
        <button
          onClick={() => window.location.reload()}
          style={{
            padding: '13px 0', borderRadius: 12,
            background: 'transparent', border: '1px solid rgba(255,255,255,0.08)',
            color: '#666', fontSize: 13,
          }}>
          Submit Another Return
        </button>
      </div>
    </div>
  )
}

export function SubmitReturn() {
  const [searchParams] = useSearchParams()
  const initialOrderId = searchParams.get('orderId') || ''
  
  const [step, setStep] = useState(1)   // 1=form, 2=submitting, 3=done
  const [claimId, setClaimId] = useState(null)
  const [form, setForm] = useState({
    orderId: initialOrderId,
    claimType: '',
    description: '',
    consentGiven: false,
    imageBase64: null,
    location: null,
  })
  const [errors, setErrors] = useState({})

  const validate = () => {
    const e = {}
    if (!form.orderId.trim())    e.orderId   = 'Order ID is required'
    if (!form.claimType)         e.claimType = 'Please select a reason'
    if (!form.consentGiven)      e.consent   = 'You must agree to proceed'
    if (!form.imageBase64)       e.image     = 'You must capture a live photo of the item'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validate()) return

    setStep(2)

    try {
      const payload = {
        orderId: form.orderId,
        claimType: form.claimType,
        description: form.description,
        image_base64: form.imageBase64,
        consent_given: true,
        accountId: 'CUST-INNOCENT-001',  // Using demo account ID
        location: form.location,
      }

      // Try real API, fallback gracefully for demo
      let id = null
      try {
        const res = await fetch('/api/v1/returns', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        if (res.ok) {
          const data = await res.json()
          id = data.claimId || data.claim_id
        }
      } catch {
        // Demo mode — API not running
        await new Promise(r => setTimeout(r, 1800))
      }

      setClaimId(id)
      setStep(3)
    } catch (err) {
      setStep(1)
      alert('Something went wrong. Please try again.')
    }
  }

  if (step === 3) return <SuccessScreen claimId={claimId} />

  return (
    <div style={{ width: '100%', maxWidth: 540, padding: '0 24px 48px' }}>
      <div style={{ marginBottom: 36 }}>
        <h1 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8, letterSpacing: -0.5 }}>
          Start a Return
        </h1>
        <p style={{ color: '#666', fontSize: 14 }}>
          Easy, hassle-free returns. Most refunds processed automatically in minutes.
        </p>
      </div>

      {/* DPDPA Consent Banner */}
      <div style={{
        padding: '12px 16px', borderRadius: 10, marginBottom: 28,
        background: 'rgba(0,212,170,0.06)', border: '1px solid rgba(0,212,170,0.15)',
        display: 'flex', gap: 10, alignItems: 'flex-start',
      }}>
        <AlertCircle size={15} color="#00D4AA" style={{ marginTop: 1, flexShrink: 0 }} />
        <p style={{ fontSize: 12, color: '#777', lineHeight: 1.6 }}>
          We analyze return data to protect all customers from fraud and ensure fair service.
          By submitting, you agree to our{' '}
          <a href="/privacy" style={{ color: '#00D4AA' }}>Return Verification Policy</a>.
          <strong style={{ color: '#999', display: 'block', marginTop: 4 }}>
            We never share your data with third parties.
          </strong>
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <CameraCapture 
          image={form.imageBase64}
          onCapture={(base64, location) => { setForm(f => ({ ...f, imageBase64: base64, location })); setErrors(er => ({ ...er, image: '' })) }}
          onRetake={() => setForm(f => ({ ...f, imageBase64: null, location: null }))}
        />
        {errors.image && <div style={{ fontSize: 13, color: '#FF6644', marginBottom: 20, textAlign: 'center' }}>{errors.image}</div>}

        {/* Order ID */}
        <FormField label="Order ID" required hint="Find this in your order confirmation email">
          <input
            type="text"
            value={form.orderId}
            onChange={e => { setForm(f => ({ ...f, orderId: e.target.value })); setErrors(er => ({ ...er, orderId: '' })) }}
            placeholder="e.g. ORD-2024-78901"
            style={{ padding: '12px 16px', fontSize: 14 }}
          />
          {errors.orderId && <div style={{ fontSize: 11, color: '#FF6644', marginTop: 5 }}>{errors.orderId}</div>}
        </FormField>

        {/* Claim Type */}
        <FormField label="Reason for Return" required>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {CLAIM_TYPES.map(ct => (
              <label key={ct.value} style={{
                padding: '12px 14px', borderRadius: 10, cursor: 'pointer',
                border: `1px solid ${form.claimType === ct.value ? 'rgba(0,212,170,0.4)' : 'rgba(255,255,255,0.07)'}`,
                background: form.claimType === ct.value ? 'rgba(0,212,170,0.08)' : 'rgba(255,255,255,0.02)',
                transition: 'all 0.15s',
              }}>
                <input
                  type="radio" name="claimType" value={ct.value}
                  style={{ display: 'none' }}
                  onChange={() => { setForm(f => ({ ...f, claimType: ct.value })); setErrors(er => ({ ...er, claimType: '' })) }}
                />
                <div style={{ fontSize: 13, fontWeight: 500, color: form.claimType === ct.value ? '#00D4AA' : '#ccc', marginBottom: 2 }}>
                  {ct.label}
                </div>
                <div style={{ fontSize: 11, color: '#555' }}>{ct.desc}</div>
              </label>
            ))}
          </div>
          {errors.claimType && <div style={{ fontSize: 11, color: '#FF6644', marginTop: 5 }}>{errors.claimType}</div>}
        </FormField>

        {/* Description */}
        <FormField label="Describe the Issue" hint="Optional — more detail helps us process faster">
          <textarea
            rows={4}
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            placeholder="Tell us what happened with your order..."
            style={{ padding: '12px 16px', fontSize: 14, resize: 'vertical', minHeight: 100 }}
          />
        </FormField>

        {/* Consent Checkbox */}
        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'flex', gap: 12, cursor: 'pointer', alignItems: 'flex-start' }}>
            <div
              onClick={() => { setForm(f => ({ ...f, consentGiven: !f.consentGiven })); setErrors(er => ({ ...er, consent: '' })) }}
              style={{
                width: 20, height: 20, borderRadius: 5, flexShrink: 0, marginTop: 1,
                border: `2px solid ${form.consentGiven ? '#00D4AA' : 'rgba(255,255,255,0.2)'}`,
                background: form.consentGiven ? 'rgba(0,212,170,0.2)' : 'transparent',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                transition: 'all 0.15s',
              }}>
              {form.consentGiven && <CheckCircle size={12} color="#00D4AA" />}
            </div>
            <span style={{ fontSize: 13, color: '#777', lineHeight: 1.5 }}>
              I understand that TriNetra AI may verify my return request using automated analysis,
              and I consent to this processing as per the{' '}
              <a href="/privacy" style={{ color: '#00D4AA' }}>Privacy Policy</a>.
            </span>
          </label>
          {errors.consent && <div style={{ fontSize: 11, color: '#FF6644', marginTop: 6, marginLeft: 32 }}>{errors.consent}</div>}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={step === 2}
          style={{
            width: '100%', padding: '15px 0',
            background: step === 2
              ? 'rgba(0,212,170,0.1)'
              : 'linear-gradient(135deg, rgba(0,255,136,0.15) 0%, rgba(0,212,170,0.15) 100%)',
            border: `1px solid ${step === 2 ? 'rgba(0,212,170,0.2)' : 'rgba(0,212,170,0.4)'}`,
            borderRadius: 12, color: '#00D4AA',
            fontSize: 14, fontWeight: 600,
            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
          }}>
          {step === 2
            ? <><span className="spinner" style={{ width: 18, height: 18, borderTopColor: '#00D4AA' }} /> Processing...</>
            : '→ Submit Return Request'}
        </button>
      </form>
    </div>
  )
}

export default SubmitReturn
