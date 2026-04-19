import { useState, useEffect } from 'react';

const API_URL = 'http://127.0.0.1:8000';

export default function ClientsPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [formData, setFormData] = useState({ name: '', phone: '', email: '' });

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const res = await fetch(`${API_URL}/clients`);
      const data = await res.json();
      setClients(data);
    } catch {
      setError('Failed to fetch clients');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const url = editingClient ? `${API_URL}/clients/${editingClient.id}` : `${API_URL}/clients`;
      const method = editingClient ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!res.ok) throw new Error('Failed to save client');
      await fetchClients();
      closeModal();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this client?')) return;
    try {
      await fetch(`${API_URL}/clients/${id}`, { method: 'DELETE' });
      await fetchClients();
    } catch {
      setError('Failed to delete client');
    }
  };

  const openModal = (client = null) => {
    setEditingClient(client);
    setFormData(client || { name: '', phone: '', email: '' });
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingClient(null);
    setFormData({ name: '', phone: '', email: '' });
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Clients</h2>
        <button className="btn btn-primary" onClick={() => openModal()}>+ Add Client</button>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="card">
        {clients.length === 0 ? (
          <div className="empty-state">
            <h3>No clients yet</h3>
            <p>Add your first client to get started</p>
          </div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Email</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {clients.map((client) => (
                <tr key={client.id}>
                  <td>{client.id}</td>
                  <td>{client.name}</td>
                  <td>{client.phone}</td>
                  <td>{client.email}</td>
                  <td className="actions">
                    <button className="btn btn-secondary btn-small" onClick={() => openModal(client)}>Edit</button>
                    <button className="btn btn-danger btn-small" onClick={() => handleDelete(client.id)}>Delete</button>
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
            <h3>{editingClient ? 'Edit Client' : 'Add Client'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
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
