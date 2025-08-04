import React, { useState, useEffect } from 'react';

// The main App component for the customer dashboard
export default function App() {
  // State to hold the list of customers fetched from the API
  const [customers, setCustomers] = useState([]);
  // State for the currently displayed, filtered customers
  const [filteredCustomers, setFilteredCustomers] = useState([]);
  // State for the search input value
  const [searchQuery, setSearchQuery] = useState('');
  // State to handle loading status
  const [isLoading, setIsLoading] = useState(true);
  // State to handle any API errors
  const [error, setError] = useState(null);

  // useEffect hook to fetch customer data from the API when the component mounts
  useEffect(() => {
    // The base URL for the Flask API
    const API_URL = 'http://127.0.0.1:5000/api/customers';

    const fetchCustomers = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        // Set the fetched customer data and stop loading
        setCustomers(data.customers);
        setFilteredCustomers(data.customers);
      } catch (e) {
        // Set the error state if the fetch fails
        setError(e.message);
      } finally {
        // Always set loading to false after the operation is complete
        setIsLoading(false);
      }
    };

    fetchCustomers();
  }, []);

  // useEffect hook to filter customers whenever the search query or the customer list changes
  useEffect(() => {
    const lowercasedQuery = searchQuery.toLowerCase();
    const results = customers.filter(customer =>
      customer.first_name.toLowerCase().includes(lowercasedQuery) ||
      customer.last_name.toLowerCase().includes(lowercasedQuery) ||
      customer.email.toLowerCase().includes(lowercasedQuery)
    );
    setFilteredCustomers(results);
  }, [searchQuery, customers]);

  // Handle the change event for the search input
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };

  // Conditional rendering for different states (loading, error, data)
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="text-xl font-semibold text-gray-700">Loading customers...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
        <div className="p-6 bg-white rounded-lg shadow-md text-red-600 font-semibold">
          Error fetching data: {error}. Please ensure your Flask API is running.
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-6 flex flex-col items-center">
      <div className="w-full max-w-7xl bg-white p-8 rounded-xl shadow-2xl">
        <h1 className="text-4xl font-extrabold text-gray-800 mb-6 text-center">Customer Dashboard</h1>

        {/* Search input field */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search by name or email..."
            value={searchQuery}
            onChange={handleSearchChange}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition duration-200"
          />
        </div>

        {/* Table to display customer data */}
        <div className="overflow-x-auto rounded-lg shadow-md">
          <table className="min-w-full bg-white">
            <thead className="bg-gray-200 text-gray-600 uppercase text-sm leading-normal">
              <tr>
                <th className="py-3 px-6 text-left">Customer ID</th>
                <th className="py-3 px-6 text-left">First Name</th>
                <th className="py-3 px-6 text-left">Last Name</th>
                <th className="py-3 px-6 text-left">Email</th>
                <th className="py-3 px-6 text-left">Created At</th>
              </tr>
            </thead>
            <tbody className="text-gray-600 text-sm font-light">
              {filteredCustomers.length > 0 ? (
                filteredCustomers.map(customer => (
                  <tr key={customer.user_id} className="border-b border-gray-200 hover:bg-gray-100 transition duration-200">
                    <td className="py-3 px-6 text-left whitespace-nowrap">{customer.user_id}</td>
                    <td className="py-3 px-6 text-left">{customer.first_name}</td>
                    <td className="py-3 px-6 text-left">{customer.last_name}</td>
                    <td className="py-3 px-6 text-left">{customer.email}</td>
                    <td className="py-3 px-6 text-left">{new Date(customer.created_at).toLocaleDateString()}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center py-4 text-gray-500">
                    No customers found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
