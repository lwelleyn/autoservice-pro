import { useState, useEffect } from 'react';

const API_URL = 'http://127.0.0.1:8000';

export default function CarsPage() {
  const [cars, setCars] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCar, setEditingCar] = useState(null);
  const [formData, setFormData] = useState({ client_id: '', brand: '', model: '', year: '', vin: '' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [carsRes, clientsRes] = await Promise.all([
        fetch(`${API_URL}/cars`),
        fetch(`${API_URL}/clients`),
      ]);
      const carsData = await carsRes.json();
      const clientsData = await clientsRes.json();
      setCars(carsData);
      setClients(clientsData);
    } catch {
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  const getClientName = (clientId) => {
    const client = clients.find((c) => c.id === clientId);
    return client ? client.name : 'Unknown';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const payload = { ...formData, year: parseInt(formData.year), client_id: parseInt(formData.client_id) };
      const url = editingCar ? `${API_URL}/cars/${editingCar.id}` : `${API_URL}/cars`;
      const method = editingCar ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error('Failed to save car');
      await fetchData();
      closeModal();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this car?')) return;
    try {
      await fetch(`${API_URL}/cars/${id}`, { method: 'DELETE' });
      await fetchData();
    } catch {
      setError('Failed to delete car');
    }
  };

  const openModal = (car = null) => {
    setEditingCar(car);
    setFormData(car || { client_id: clients.length > 0 ? clients[0].id : '', brand: '', model: '', year: '', vin: '' });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingCar(null);
    setFormData({ client_id: '', brand: '', model: '', year: '', vin: '' });
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Cars</h2>
        <button className="btn btn-primary" onClick={() => openModal()} disabled={clients.length === 0}>+ Add Car</button>
      </div>

      {clients.length === 0 && (
        <div className="error" style={{ background: '#fef3c7', color: '#92400e' }}>
          Add a client first before adding cars
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <div className="card">
        {cars.length === 0 ? (
          <div className="empty-state">
            <h3>No cars yet</h3>
            <p>Add your first car to get started</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Brand</th>
                <th>Model</th>
                <th>Year</th>
                <th>VIN</th>
                <th>Owner</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {cars.map((car) => (
                <tr key={car.id}>
                  <td>{car.id}</td>
                  <td>{car.brand}</td>
                  <td>{car.model}</td>
                  <td>{car.year}</td>
                  <td>{car.vin}</td>
                  <td>{getClientName(car.client_id)}</td>
                  <td className="actions">
                    <button className="btn btn-secondary btn-small" onClick={() => openModal(car)}>Edit</button>
                    <button className="btn btn-danger btn-small" onClick={() => handleDelete(car.id)}>Delete</button>
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
            <h3>{editingCar ? 'Edit Car' : 'Add Car'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Owner</label>
                <select
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                  required
                >
                  {clients.map((client) => (
                    <option key={client.id} value={client.id}>{client.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Brand</label>
                <input
                  type="text"
                  value={formData.brand}
                  onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Model</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Year</label>
                <input
                  type="number"
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                  min="1900"
                  max="2030"
                  required
                />
              </div>
              <div className="form-group">
                <label>VIN</label>
                <input
                  type="text"
                  value={formData.vin}
                  onChange={(e) => setFormData({ ...formData, vin: e.target.value })}
                  maxLength="17"
                  required
                />
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
