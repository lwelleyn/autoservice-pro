import { useState, useEffect } from 'react';

const API_URL = 'http://127.0.0.1:8000';

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

export default function WorkOrdersPage() {
  const [workOrders, setWorkOrders] = useState([]);
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const [formData, setFormData] = useState({ car_id: '', description: '', status: 'pending' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [ordersRes, carsRes] = await Promise.all([
        fetch(`${API_URL}/work-orders`),
        fetch(`${API_URL}/cars`),
      ]);
      const ordersData = await ordersRes.json();
      const carsData = await carsRes.json();
      setWorkOrders(ordersData);
      setCars(carsData);
    } catch {
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const getCarInfo = (carId) => {
    const car = cars.find((c) => c.id === carId);
    return car ? `${car.brand} ${car.model} (${car.year})` : 'Unknown';
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'pending': return 'status-pending';
      case 'in_progress': return 'status-in-progress';
      case 'completed': return 'status-completed';
      case 'cancelled': return 'status-cancelled';
      default: return '';
    }
  };

  const getStatusLabel = (status) => {
    const opt = STATUS_OPTIONS.find((o) => o.value === status);
    return opt ? opt.label : status;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const payload = { ...formData, car_id: parseInt(formData.car_id) };
      const url = editingOrder ? `${API_URL}/work-orders/${editingOrder.id}` : `${API_URL}/work-orders`;
      const method = editingOrder ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to save work order');
      await fetchData();
      closeModal();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this work order?')) return;
    try {
      await fetch(`${API_URL}/work-orders/${id}`, { method: 'DELETE' });
      await fetchData();
    } catch {
      setError('Failed to delete work order');
    }
  };

  const openModal = (order = null) => {
    setEditingOrder(order);
    setFormData(order || { car_id: cars.length > 0 ? cars[0].id : '', description: '', status: 'pending' });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingOrder(null);
    setFormData({ car_id: '', description: '', status: 'pending' });
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Work Orders</h2>
        <button className="btn btn-primary" onClick={() => openModal()} disabled={cars.length === 0}>+ Add Work Order</button>
      </div>

      {cars.length === 0 && (
        <div className="error" style={{ background: '#fef3c7', color: '#92400e' }}>
          Add a car first before creating work orders
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <div className="card">
        {workOrders.length === 0 ? (
          <div className="empty-state">
            <h3>No work orders yet</h3>
            <p>Create your first work order to get started</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Car</th>
                <th>Description</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {workOrders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>{getCarInfo(order.car_id)}</td>
                  <td>{order.description}</td>
                  <td>
                    <span className={`status-badge ${getStatusClass(order.status)}`}>
                      {getStatusLabel(order.status)}
                    </span>
                  </td>
                  <td>{new Date(order.created_at).toLocaleDateString()}</td>
                  <td className="actions">
                    <button className="btn btn-secondary btn-small" onClick={() => openModal(order)}>Edit</button>
                    <button className="btn btn-danger btn-small" onClick={() => handleDelete(order.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingOrder ? 'Edit Work Order' : 'Add Work Order'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Car</label>
                <select
                  value={formData.car_id}
                  onChange={(e) => setFormData({ ...formData, car_id: e.target.value })}
                  required
                >
                  {cars.map((car) => (
                    <option key={car.id} value={car.id}>
                      {car.brand} {car.model} ({car.year})
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  required
                />
              </div>
              <div className="form-group">
                <label>Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                  required
                >
                  {STATUS_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={closeModal}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}