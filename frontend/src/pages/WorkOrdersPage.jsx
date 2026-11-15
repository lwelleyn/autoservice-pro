import { useState, useEffect } from 'react';
import { carsApi, workOrdersApi } from '../api';

const STATUS_OPTIONS = [
  { value: 'pending', label: 'Pending' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

const EMPTY_FORM = { car_id: '', description: '', status: 'pending' };

export default function WorkOrdersPage() {
  const [workOrders, setWorkOrders] = useState([]);
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  const fetchData = async () => {
    try {
      const [ordersData, carsData] = await Promise.all([workOrdersApi.list(), carsApi.list()]);
      setWorkOrders(ordersData);
      setCars(carsData);
      setLoadError('');
    } catch (e) {
      setLoadError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

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
    setFormError('');
    setSaving(true);
    // Send only the fields the API expects.
    const payload = {
      car_id: Number(formData.car_id),
      description: formData.description.trim(),
      status: formData.status,
    };
    try {
      if (editingOrder) {
        await workOrdersApi.update(editingOrder.id, payload);
      } else {
        await workOrdersApi.create(payload);
      }
      closeModal();
      await fetchData();
    } catch (e) {
      setFormError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (order) => {
    if (!confirm(`Delete work order #${order.id}? This cannot be undone.`)) return;
    setError('');
    try {
      await workOrdersApi.remove(order.id);
      await fetchData();
    } catch (e) {
      setError(`Failed to delete work order: ${e.message}`);
    }
  };

  const openModal = (order = null) => {
    setEditingOrder(order);
    setFormData(
      order
        ? { car_id: order.car_id, description: order.description, status: order.status }
        : { ...EMPTY_FORM, car_id: cars.length > 0 ? cars[0].id : '' }
    );
    setFormError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingOrder(null);
    setFormData(EMPTY_FORM);
    setFormError('');
  };

  if (loading) return <div className="loading">Loading...</div>;

  const noCars = !loadError && cars.length === 0;

  return (
    <div>
      <div className="page-header">
        <h2>Work Orders</h2>
        <button className="btn btn-primary" onClick={() => openModal()} disabled={!!loadError || noCars}>
          + Add Work Order
        </button>
      </div>

      {noCars && <div className="warning">Add a car first before creating work orders</div>}

      {error && <div className="error">{error}</div>}

      {loadError ? (
        <div className="error">
          Failed to load work orders: {loadError}{' '}
          <button className="btn btn-secondary btn-small" onClick={fetchData}>Retry</button>
        </div>
      ) : (
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
                      <button className="btn btn-danger btn-small" onClick={() => handleDelete(order)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingOrder ? 'Edit Work Order' : 'Add Work Order'}</h3>
            {formError && <div className="error">{formError}</div>}
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
                  maxLength={500}
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
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
