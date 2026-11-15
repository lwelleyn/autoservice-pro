import { useState, useEffect } from 'react';
import { clientsApi } from '../api';

const EMPTY_FORM = { name: '', phone: '', email: '' };

export default function ClientsPage() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');
  const [error, setError] = useState('');
  const [formError, setFormError] = useState('');
  const [saving, setSaving] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  const fetchClients = async () => {
    try {
      setClients(await clientsApi.list());
      setLoadError('');
    } catch (e) {
      setLoadError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchClients();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError('');
    setSaving(true);
    // Send only the fields the API expects.
    const payload = {
      name: formData.name.trim(),
      phone: formData.phone.trim(),
      email: formData.email.trim(),
    };
    try {
      if (editingClient) {
        await clientsApi.update(editingClient.id, payload);
      } else {
        await clientsApi.create(payload);
      }
      closeModal();
      await fetchClients();
    } catch (e) {
      setFormError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (client) => {
    const message =
      `Delete client "${client.name}"?\n\n` +
      'All cars of this client and all their work orders will be deleted too. ' +
      'This cannot be undone.';
    if (!confirm(message)) return;
    setError('');
    try {
      await clientsApi.remove(client.id);
      await fetchClients();
    } catch (e) {
      setError(`Failed to delete client: ${e.message}`);
    }
  };

  const openModal = (client = null) => {
    setEditingClient(client);
    setFormData(
      client ? { name: client.name, phone: client.phone, email: client.email } : EMPTY_FORM
    );
    setFormError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingClient(null);
    setFormData(EMPTY_FORM);
    setFormError('');
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Clients</h2>
        <button className="btn btn-primary" onClick={() => openModal()} disabled={!!loadError}>
          + Add Client
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {loadError ? (
        <div className="error">
          Failed to load clients: {loadError}{' '}
          <button className="btn btn-secondary btn-small" onClick={fetchClients}>Retry</button>
        </div>
      ) : (
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
                      <button className="btn btn-danger btn-small" onClick={() => handleDelete(client)}>Delete</button>
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
            <h3>{editingClient ? 'Edit Client' : 'Add Client'}</h3>
            {formError && <div className="error">{formError}</div>}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  maxLength={100}
                  required
                />
              </div>
              <div className="form-group">
                <label>Phone</label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  maxLength={20}
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  maxLength={100}
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
