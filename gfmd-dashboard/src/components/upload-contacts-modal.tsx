'use client';

import { useState, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface UploadResult {
  success: boolean;
  imported: number;
  duplicates: number;
  sequencesStarted: number;
  totalProcessed: number;
  errors: number;
  errorDetails?: string[];
  error?: string;
}

interface UploadContactsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UploadContactsModal({ isOpen, onClose }: UploadContactsModalProps) {
  const [file, setFile] = useState<File | null>(null);
  const [startSequences, setStartSequences] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setResult(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('startSequences', startSequences.toString());

      const response = await fetch('/api/upload-contacts', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setResult(data);

    } catch (error) {
      setResult({
        success: false,
        imported: 0,
        duplicates: 0,
        sequencesStarted: 0,
        totalProcessed: 0,
        errors: 1,
        error: 'Failed to upload file'
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDownloadSample = async () => {
    try {
      const response = await fetch('/api/upload-contacts');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'sample_contacts.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download sample:', error);
    }
  };

  const handleClose = () => {
    setFile(null);
    setResult(null);
    setStartSequences(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-hidden">
        <div className="flex justify-between items-center p-6" style={{borderBottom: '1px solid #efebe2'}}>
          <div>
            <h2 className="text-2xl font-normal" style={{color: '#272030'}}>Upload Contacts</h2>
            <p className="text-sm font-light mt-1" style={{color: '#272030'}}>
              Import contacts from a CSV file
            </p>
          </div>
          <button
            onClick={handleClose}
            className="text-2xl font-light hover:opacity-70"
            style={{color: '#272030'}}
          >
            x
          </button>
        </div>

        <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
          {!result ? (
            <div className="space-y-6">
              {/* File Upload Area */}
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardHeader>
                  <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                    Select CSV File
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div
                    className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer hover:bg-gray-50 transition-colors"
                    style={{borderColor: '#efebe2'}}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileChange}
                      accept=".csv"
                      className="hidden"
                    />
                    {file ? (
                      <div>
                        <p className="font-normal" style={{color: '#272030'}}>{file.name}</p>
                        <p className="text-sm font-light mt-1" style={{color: '#272030'}}>
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="font-normal" style={{color: '#272030'}}>
                          Click to select a CSV file
                        </p>
                        <p className="text-sm font-light mt-1" style={{color: '#272030'}}>
                          or drag and drop
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Options */}
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardHeader>
                  <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                    Options
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={startSequences}
                      onChange={(e) => setStartSequences(e.target.checked)}
                      className="w-4 h-4 rounded"
                      style={{accentColor: '#4e2780'}}
                    />
                    <div>
                      <p className="font-normal" style={{color: '#272030'}}>
                        Start email sequences immediately
                      </p>
                      <p className="text-sm font-light" style={{color: '#272030'}}>
                        Contacts will begin receiving outreach emails
                      </p>
                    </div>
                  </label>
                </CardContent>
              </Card>

              {/* Expected Format */}
              <Card style={{borderColor: '#efebe2', backgroundColor: '#ffffff'}}>
                <CardHeader>
                  <CardTitle className="text-lg font-normal" style={{color: '#272030'}}>
                    Expected CSV Format
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm font-light mb-3" style={{color: '#272030'}}>
                    Your CSV should have columns for contact information. Required: email
                  </p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm" style={{borderColor: '#efebe2'}}>
                      <thead>
                        <tr style={{backgroundColor: '#efebe2'}}>
                          <th className="p-2 text-left font-normal" style={{color: '#272030'}}>name</th>
                          <th className="p-2 text-left font-normal" style={{color: '#272030'}}>email</th>
                          <th className="p-2 text-left font-normal" style={{color: '#272030'}}>organization</th>
                          <th className="p-2 text-left font-normal" style={{color: '#272030'}}>title</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td className="p-2 font-light" style={{color: '#272030', borderTop: '1px solid #efebe2'}}>John Smith</td>
                          <td className="p-2 font-light" style={{color: '#272030', borderTop: '1px solid #efebe2'}}>john@police.gov</td>
                          <td className="p-2 font-light" style={{color: '#272030', borderTop: '1px solid #efebe2'}}>City PD</td>
                          <td className="p-2 font-light" style={{color: '#272030', borderTop: '1px solid #efebe2'}}>Chief</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                  <button
                    onClick={handleDownloadSample}
                    className="mt-3 text-sm font-normal hover:underline"
                    style={{color: '#4e2780'}}
                  >
                    Download sample CSV
                  </button>
                </CardContent>
              </Card>

              {/* Upload Button */}
              <div className="flex gap-3">
                <button
                  onClick={handleClose}
                  className="flex-1 px-4 py-3 rounded font-normal border hover:bg-gray-50"
                  style={{borderColor: '#efebe2', color: '#272030'}}
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  className="flex-1 px-4 py-3 rounded font-normal text-white disabled:opacity-50"
                  style={{backgroundColor: '#4e2780'}}
                >
                  {uploading ? 'Uploading...' : 'Upload Contacts'}
                </button>
              </div>
            </div>
          ) : (
            /* Results View */
            <div className="space-y-6">
              <Card style={{
                borderColor: result.success ? '#4e2780' : '#ef4444',
                backgroundColor: '#ffffff'
              }}>
                <CardHeader>
                  <CardTitle
                    className="text-lg font-normal"
                    style={{color: result.success ? '#4e2780' : '#ef4444'}}
                  >
                    {result.success ? 'Upload Complete' : 'Upload Failed'}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {result.success ? (
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="p-3 rounded" style={{backgroundColor: '#efebe2'}}>
                          <p className="text-2xl font-normal" style={{color: '#4e2780'}}>{result.imported}</p>
                          <p className="text-sm font-light" style={{color: '#272030'}}>Contacts Imported</p>
                        </div>
                        <div className="p-3 rounded" style={{backgroundColor: '#efebe2'}}>
                          <p className="text-2xl font-normal" style={{color: '#272030'}}>{result.duplicates}</p>
                          <p className="text-sm font-light" style={{color: '#272030'}}>Duplicates Skipped</p>
                        </div>
                        {result.sequencesStarted > 0 && (
                          <div className="p-3 rounded" style={{backgroundColor: '#efebe2'}}>
                            <p className="text-2xl font-normal" style={{color: '#4e2780'}}>{result.sequencesStarted}</p>
                            <p className="text-sm font-light" style={{color: '#272030'}}>Sequences Started</p>
                          </div>
                        )}
                        {result.errors > 0 && (
                          <div className="p-3 rounded" style={{backgroundColor: '#efebe2'}}>
                            <p className="text-2xl font-normal" style={{color: '#ef4444'}}>{result.errors}</p>
                            <p className="text-sm font-light" style={{color: '#272030'}}>Errors</p>
                          </div>
                        )}
                      </div>

                      {result.errorDetails && result.errorDetails.length > 0 && (
                        <div className="mt-4">
                          <p className="text-sm font-normal mb-2" style={{color: '#272030'}}>Error Details:</p>
                          <div className="text-sm font-light p-3 rounded max-h-32 overflow-auto" style={{backgroundColor: '#efebe2', color: '#272030'}}>
                            {result.errorDetails.map((err, i) => (
                              <p key={i}>{err}</p>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="font-light" style={{color: '#272030'}}>
                      {result.error || 'An error occurred while processing the file.'}
                    </p>
                  )}
                </CardContent>
              </Card>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setFile(null);
                    setResult(null);
                  }}
                  className="flex-1 px-4 py-3 rounded font-normal border hover:bg-gray-50"
                  style={{borderColor: '#efebe2', color: '#272030'}}
                >
                  Upload Another
                </button>
                <button
                  onClick={handleClose}
                  className="flex-1 px-4 py-3 rounded font-normal text-white"
                  style={{backgroundColor: '#4e2780'}}
                >
                  Done
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
