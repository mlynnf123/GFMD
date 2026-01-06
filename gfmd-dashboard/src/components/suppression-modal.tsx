'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

interface SuppressionRecord {
  _id: string;
  email: string;
  suppressed_at: string;
  reason: string;
  source: {
    type: string;
    admin_user?: string;
  };
}

interface SuppressionStats {
  total_suppressed: number;
  recent_suppressed: number;
  by_reason: Array<{
    _id: string;
    count: number;
  }>;
}

interface SuppressionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SuppressionModal({ isOpen, onClose }: SuppressionModalProps) {
  const [suppressions, setSuppressions] = useState<SuppressionRecord[]>([]);
  const [stats, setStats] = useState<SuppressionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [newSuppressionEmail, setNewSuppressionEmail] = useState('');
  const [newSuppressionReason, setNewSuppressionReason] = useState('');
  const [isAddingSuppress, setIsAddingSuppress] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchSuppressions();
    }
  }, [isOpen, currentPage, searchTerm]);

  const fetchSuppressions = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20'
      });
      
      if (searchTerm) {
        params.append('search', searchTerm);
      }
      
      const response = await fetch(`/api/suppression-list?${params}`);
      const data = await response.json();
      
      setSuppressions(data.suppressed_contacts || []);
      setStats(data.stats || null);
      setTotalPages(data.pagination?.total_pages || 1);
    } catch (error) {
      console.error('Error fetching suppressions:', error);
    } finally {
      setLoading(false);
    }
  };

  const addSuppression = async () => {
    if (!newSuppressionEmail || !newSuppressionReason) {
      alert('Please enter both email and reason');
      return;
    }

    try {
      setIsAddingSuppress(true);
      const response = await fetch('/api/suppression-list', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: newSuppressionEmail,
          reason: newSuppressionReason,
          admin_user: 'dashboard_user'
        })
      });

      const result = await response.json();
      
      if (response.ok) {
        setNewSuppressionEmail('');
        setNewSuppressionReason('');
        fetchSuppressions(); // Refresh list
        alert('Contact successfully suppressed');
      } else {
        alert(result.error || 'Failed to add suppression');
      }
    } catch (error) {
      alert('Error adding suppression');
      console.error(error);
    } finally {
      setIsAddingSuppress(false);
    }
  };

  const removeSuppression = async (email: string) => {
    if (!confirm(`Are you sure you want to unsuppress ${email}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/suppression-list?email=${encodeURIComponent(email)}`, {
        method: 'DELETE'
      });

      const result = await response.json();
      
      if (response.ok) {
        fetchSuppressions(); // Refresh list
        alert('Contact successfully unsuppressed');
      } else {
        alert(result.error || 'Failed to remove suppression');
      }
    } catch (error) {
      alert('Error removing suppression');
      console.error(error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6" style={{borderBottom: '1px solid #efebe2'}}>
          <h2 className="text-2xl font-normal" style={{color: '#272030'}}>Email Suppression List</h2>
          <button
            onClick={onClose}
            className="text-2xl font-light hover:opacity-70"
            style={{color: '#272030'}}
          >
            ×
          </button>
        </div>
        
        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          {/* Stats Cards */}
          {stats && (
            <div className="grid gap-4 md:grid-cols-3 mb-6">
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardContent className="p-4">
                  <div className="text-2xl font-normal" style={{color: '#272030'}}>
                    {stats.total_suppressed}
                  </div>
                  <p className="text-sm font-light" style={{color: '#272030'}}>
                    Total Suppressed
                  </p>
                </CardContent>
              </Card>
              
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardContent className="p-4">
                  <div className="text-2xl font-normal" style={{color: '#272030'}}>
                    {stats.recent_suppressed}
                  </div>
                  <p className="text-sm font-light" style={{color: '#272030'}}>
                    Last 7 Days
                  </p>
                </CardContent>
              </Card>
              
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardContent className="p-4">
                  <div className="text-2xl font-normal" style={{color: '#272030'}}>
                    {stats.by_reason.length}
                  </div>
                  <p className="text-sm font-light" style={{color: '#272030'}}>
                    Suppression Types
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Add New Suppression */}
          <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}} className="mb-6">
            <CardHeader>
              <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                Add Manual Suppression
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <input
                  type="email"
                  placeholder="Email address"
                  value={newSuppressionEmail}
                  onChange={(e) => setNewSuppressionEmail(e.target.value)}
                  className="px-3 py-2 border rounded font-light"
                  style={{borderColor: '#efebe2', color: '#272030'}}
                />
                <input
                  type="text"
                  placeholder="Reason for suppression"
                  value={newSuppressionReason}
                  onChange={(e) => setNewSuppressionReason(e.target.value)}
                  className="px-3 py-2 border rounded font-light"
                  style={{borderColor: '#efebe2', color: '#272030'}}
                />
                <button
                  onClick={addSuppression}
                  disabled={isAddingSuppress}
                  className="px-4 py-2 rounded font-normal text-white hover:opacity-90 disabled:opacity-50"
                  style={{backgroundColor: '#4e2780'}}
                >
                  {isAddingSuppress ? 'Adding...' : 'Add Suppression'}
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Search */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search by email address..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border rounded font-light"
              style={{borderColor: '#efebe2', color: '#272030'}}
            />
          </div>
          
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{borderColor: '#4e2780'}}></div>
              <span className="ml-3 font-light" style={{color: '#272030'}}>Loading suppressions...</span>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow style={{borderColor: '#efebe2'}}>
                  <TableHead className="font-light" style={{color: '#272030'}}>Email</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Reason</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Source</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Suppressed Date</TableHead>
                  <TableHead className="font-light" style={{color: '#272030'}}>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {suppressions.map((suppression) => (
                  <TableRow key={suppression._id} style={{borderColor: '#efebe2'}}>
                    <TableCell className="font-normal" style={{color: '#272030'}}>
                      {suppression.email}
                    </TableCell>
                    <TableCell className="font-light" style={{color: '#272030'}}>
                      {suppression.reason}
                    </TableCell>
                    <TableCell className="font-light" style={{color: '#272030'}}>
                      <span 
                        className="px-2 py-1 rounded text-xs font-light"
                        style={{
                          backgroundColor: suppression.source.type === 'manual_admin' ? '#4e2780' : '#efebe2',
                          color: suppression.source.type === 'manual_admin' ? 'white' : '#272030'
                        }}
                      >
                        {suppression.source.type}
                      </span>
                    </TableCell>
                    <TableCell className="font-light" style={{color: '#272030'}}>
                      {new Date(suppression.suppressed_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <button
                        onClick={() => removeSuppression(suppression.email)}
                        className="px-3 py-1 rounded text-sm font-light hover:opacity-70"
                        style={{backgroundColor: '#272030', color: 'white'}}
                      >
                        Unsuppress
                      </button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
          
          {!loading && suppressions.length === 0 && (
            <div className="text-center py-12">
              <p className="font-light" style={{color: '#272030'}}>No suppressed contacts found</p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2 mt-6">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 rounded font-light disabled:opacity-50"
                style={{backgroundColor: '#efebe2', color: '#272030'}}
              >
                Previous
              </button>
              
              <span className="px-3 py-1 font-light" style={{color: '#272030'}}>
                Page {currentPage} of {totalPages}
              </span>
              
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 rounded font-light disabled:opacity-50"
                style={{backgroundColor: '#efebe2', color: '#272030'}}
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}