import { useState, useEffect } from 'react';
import { carsApi, clientsApi } from '../api';

const EMPTY_FORM = { client_id: '', brand: '', model: '', year: '', vin: '' };
const MIN_YEAR = 1900;
const MAX_YEAR = new Date().getFullYear() + 1;
// 17 characters: digits and Latin letters except I, O, Q (same rule as the backend).
const VIN_PATTERN = '[A-HJ-NPR-Za-hj-npr-z0-9]{17}';

export default function CarsPage() {
  const [cars, setCars] = useState([]);
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingCar, setEditingCar] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  const fetchData = async () => {
    try {
      const [carsData, clientsData] = await Promise.all([carsApi.list(), clientsApi.list()]);
      setCars(carsData);
      setClients(clientsData);
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

  const getClientName = (clientId) => {
    const client = clients.find((c) => c.id === clientId);
    return client ? client.name : 'Unknown';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setSaving(true);
    // Send only the fields the API expects.
    const payload = {
      client_id: Number(formData.client_id),
      brand: formData.brand.trim(),
      model: formData.model.trim(),
      year: Number(formData.year),
      vin: formData.vin.trim().toUpperCase(),
    };
    try {
      if (editingCar) {
        await carsApi.update(editingCar.id, payload);
      } else {
        await carsApi.create(payload);
      }
      closeModal();
      await fetchData();
    } catch (e) {
      setFormError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (car) => {
    const message =
      `Delete ${car.brand} ${car.model} (${car.vin})?\n\n` +
      'All work orders of this car will be deleted too. This cannot be undone.';
    if (!confirm(message)) return;
    setError('');
    try {
      await carsApi.remove(car.id);
      await fetchData();
    } catch (e) {
      setError(`Failed to delete car: ${e.message}`);
    }
  };

  const openModal = (car = null) => {
    setEditingCar(car);
    setFormData(
      car
        ? { client_id: car.client_id, brand: car.brand, model: car.model, year: car.year, vin: car.vin }
        : { ...EMPTY_FORM, client_id: clients.length > 0 ? clients[0].id : '' }
    );
    setFormError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingCar(null);
    setFormData(EMPTY_FORM);
    setFormError('');
  };

  if (loading) return <div className="loading">Loading...</div>;

  const noClients = !loadError && clients.length === 0;

  return (
    <div>
      <div className="page-header">
        <h2>Cars</h2>
        <button className="btn btn-primary" onClick={() => openModal()} disabled={!!loadError || noClients}>
          + Add Car
        </button>
      </div>

      {noClients && <div className="warning">Add a client first before adding cars</div>}

      {error && <div className="error">{error}</div>}

      {loadError ? (
        <div className="error">
          Failed to load cars: {loadError}{' '}
          <button className="btn btn-secondary btn-small" onClick={fetchData}>Retry</button>
        </div>
      ) : (
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
                      <button className="btn btn-danger btn-small" onClick={() => handleDelete(car)}>Delete</button>
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
            <h3>{editingCar ? 'Edit Car' : 'Add Car'}</h3>
            {formError && <div className="error">{formError}</div>}
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
                  maxLength={50}
                  required
                />
              </div>
              <div className="form-group">
                <label>Model</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  maxLength={50}
                  required
                />
              </div>
              <div className="form-group">
                <label>Year</label>
                <input
                  type="number"
                  value={formData.year}
                  onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                  min={MIN_YEAR}
                  max={MAX_YEAR}
                  required
                />
              </div>
              <div className="form-group">
                <label>VIN</label>
                <input
                  type="text"
                  value={formData.vin}
                  onChange={(e) => setFormData({ ...formData, vin: e.target.value })}
                  minLength={17}
                  maxLength={17}
                  pattern={VIN_PATTERN}
                  title="17 characters: digits and Latin letters except I, O, Q"
                  required
                />
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
