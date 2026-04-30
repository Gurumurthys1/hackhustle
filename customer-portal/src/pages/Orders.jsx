import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Package, Clock, ShieldCheck, ChevronRight, Plus, X, Trash2 } from 'lucide-react'

// For demo purposes, we log in as the innocent test customer
const MOCK_ACCOUNT_ID = "CUST-INNOCENT-001"

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  
  const [newOrder, setNewOrder] = useState({
    product_name: '',
    order_amount: '',
    product_image_url: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const fetchOrders = () => {
    fetch(`/api/v1/orders/${MOCK_ACCOUNT_ID}`)
      .then(res => res.json())
      .then(data => {
        if (data.orders) {
          setOrders(data.orders)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch orders:", err)
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchOrders()
  }, [])

  const handleCreateOrder = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await fetch('/api/v1/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          account_id: MOCK_ACCOUNT_ID,
          product_name: newOrder.product_name,
          order_amount: parseFloat(newOrder.order_amount) || 1000,
          product_image_url: newOrder.product_image_url
        })
      })
      setShowModal(false)
      setNewOrder({ product_name: '', order_amount: '', product_image_url: '' })
      fetchOrders() // Refresh list
    } catch (err) {
      console.error("Error creating order", err)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteOrder = async (orderId) => {
    try {
      await fetch(`/api/v1/orders/${orderId}`, {
        method: 'DELETE'
      })
      fetchOrders()
    } catch (err) {
      console.error("Error deleting order", err)
    }
  }



  if (loading) {
    return (
      <div style={{ padding: '40px', color: '#888', fontFamily: 'Space Mono, monospace' }}>
        LOADING ORDERS...
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 800, width: '100%', padding: '0 20px', fontFamily: 'Sora, sans-serif' }}>
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 28, color: '#fff', marginBottom: 8 }}>My Orders</h1>
          <p style={{ color: '#888', fontSize: 14 }}>View your purchase history and manage returns.</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '10px 16px', background: 'rgba(0,255,136,0.1)',
            border: '1px solid rgba(0,255,136,0.3)', borderRadius: 10,
            color: '#00FF88', fontSize: 13, fontWeight: 600, cursor: 'pointer',
            transition: 'all 0.2s'
          }}
          onMouseOver={e => e.currentTarget.style.background = 'rgba(0,255,136,0.2)'}
          onMouseOut={e => e.currentTarget.style.background = 'rgba(0,255,136,0.1)'}
        >
          <Plus size={16} /> Add Dummy Order
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {orders.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#555', background: 'rgba(255,255,255,0.02)', borderRadius: 16, border: '1px solid rgba(255,255,255,0.05)' }}>
            <Package size={32} style={{ marginBottom: 16, opacity: 0.5 }} />
            <div>No recent orders found.</div>
          </div>
        ) : (
          orders.map(order => (
            <div key={order.id} style={{
              background: 'rgba(255,255,255,0.03)',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: 16,
              padding: 20,
              display: 'flex',
              gap: 24,
              alignItems: 'center',
              transition: 'all 0.2s',
            }}>
              {/* Product Image */}
              <div style={{ 
                width: 100, height: 100, borderRadius: 12, overflow: 'hidden', 
                border: '1px solid rgba(255,255,255,0.1)', flexShrink: 0,
                background: 'rgba(0,0,0,0.5)'
              }}>
                <img 
                  src={order.product_image_url || "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&q=80"} 
                  alt={order.product_name}
                  style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                />
              </div>

              {/* Details */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                  <h3 style={{ margin: 0, fontSize: 16, color: '#fff', fontWeight: 600 }}>
                    {order.product_name}
                  </h3>
                  <div style={{ fontFamily: 'Space Mono, monospace', fontSize: 15, color: '#00FF88', fontWeight: 700 }}>
                    ₹{Number(order.order_amount).toLocaleString('en-IN')}
                  </div>
                </div>
                
                <div style={{ display: 'flex', gap: 16, color: '#888', fontSize: 12, marginBottom: 12, fontFamily: 'Space Mono, monospace' }}>
                  <div>Order ID: {order.id}</div>
                  <div>•</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <Clock size={12} /> {new Date(order.ordered_at).toLocaleDateString()}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                  <span style={{ 
                    padding: '4px 10px', background: 'rgba(0,212,170,0.1)', 
                    color: '#00D4AA', borderRadius: 6, fontSize: 11, fontWeight: 600 
                  }}>
                    DELIVERED
                  </span>
                  <span style={{ 
                    padding: '4px 10px', background: 'rgba(255,255,255,0.05)', 
                    color: '#aaa', borderRadius: 6, fontSize: 11
                  }}>
                    {order.carrier_name}
                  </span>
                </div>
              </div>

              {/* Action */}
              <div style={{ paddingLeft: 20, borderLeft: '1px solid rgba(255,255,255,0.08)', display: 'flex', alignItems: 'center', gap: 12 }}>
                <Link to={`/return?orderId=${order.id}`} style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '12px 20px', background: '#fff', color: '#000',
                  borderRadius: 10, fontSize: 13, fontWeight: 600,
                  textDecoration: 'none', transition: 'all 0.2s',
                  boxShadow: '0 4px 12px rgba(255,255,255,0.1)'
                }}
                onMouseOver={e => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseOut={e => e.currentTarget.style.transform = 'none'}
                >
                  Return Item
                  <ChevronRight size={16} />
                </Link>
                
                {order.id.startsWith('ord-demo') && (
                  <button 
                    onClick={() => handleDeleteOrder(order.id)}
                    style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      width: 40, height: 40, borderRadius: 10,
                      background: 'rgba(255,68,68,0.1)', border: '1px solid rgba(255,68,68,0.3)',
                      color: '#FF4444', cursor: 'pointer', transition: 'all 0.2s'
                    }}
                    title="Delete Dummy Order"
                    onMouseOver={e => e.currentTarget.style.background = 'rgba(255,68,68,0.2)'}
                    onMouseOut={e => e.currentTarget.style.background = 'rgba(255,68,68,0.1)'}
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div style={{
            background: '#0B0F19', border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 16, width: 400, padding: 24, position: 'relative'
          }}>
            <button 
              onClick={() => setShowModal(false)}
              style={{ position: 'absolute', top: 16, right: 16, background: 'transparent', border: 'none', color: '#888', cursor: 'pointer' }}
            >
              <X size={20} />
            </button>
            <h2 style={{ fontSize: 20, color: '#fff', marginBottom: 20 }}>Create Dummy Order</h2>
            <form onSubmit={handleCreateOrder} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <div>
                <label style={{ display: 'block', color: '#ccc', fontSize: 13, marginBottom: 8 }}>Product Name</label>
                <input 
                  required
                  type="text" 
                  value={newOrder.product_name}
                  onChange={e => setNewOrder({...newOrder, product_name: e.target.value})}
                  placeholder="e.g. Rolex Submariner"
                  style={{ width: '100%', padding: '10px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', outline: 'none' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', color: '#ccc', fontSize: 13, marginBottom: 8 }}>Price (INR)</label>
                <input 
                  required
                  type="number" 
                  value={newOrder.order_amount}
                  onChange={e => setNewOrder({...newOrder, order_amount: e.target.value})}
                  placeholder="e.g. 15000"
                  style={{ width: '100%', padding: '10px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', outline: 'none' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', color: '#ccc', fontSize: 13, marginBottom: 8 }}>Product Image URL</label>
                <input 
                  required
                  type="url" 
                  value={newOrder.product_image_url}
                  onChange={e => setNewOrder({...newOrder, product_image_url: e.target.value})}
                  placeholder="Paste any image link here"
                  style={{ width: '100%', padding: '10px', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: '#fff', outline: 'none' }}
                />
              </div>
              <button 
                type="submit" 
                disabled={isSubmitting}
                style={{
                  marginTop: 8, padding: '12px', background: '#00FF88', color: '#000', 
                  borderRadius: 8, fontWeight: 600, fontSize: 14, border: 'none', cursor: 'pointer',
                  opacity: isSubmitting ? 0.7 : 1
                }}
              >
                {isSubmitting ? 'Creating...' : 'Create Order'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
