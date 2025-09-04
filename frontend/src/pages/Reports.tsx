import React, { useState } from 'react';
import { FileText, Download, Plus, Calendar, Filter } from 'lucide-react';
import { Report } from '../types';

const Reports: React.FC = () => {
  const [reports] = useState<Report[]>([
    {
      id: '1',
      title: 'Rapport environnemental mensuel - Janvier 2025',
      type: 'environmental',
      generatedAt: '2025-01-15T10:30:00Z',
      generatedBy: 'John Doe',
      status: 'published',
      summary: 'Analyse complète des données environnementales collectées en janvier.',
      downloadUrl: '/reports/january-2025.pdf',
    },
    {
      id: '2',
      title: 'Rapport de maintenance des capteurs',
      type: 'maintenance',
      generatedAt: '2025-01-10T14:20:00Z',
      generatedBy: 'Jane Smith',
      status: 'published',
      summary: 'État de maintenance et recommandations pour tous les capteurs.',
      downloadUrl: '/reports/maintenance-january.pdf',
    },
    {
      id: '3',
      title: 'Analyse de tendances - Q4 2024',
      type: 'analysis',
      generatedAt: '2025-01-05T09:15:00Z',
      generatedBy: 'Mike Johnson',
      status: 'draft',
      summary: 'Analyse des tendances environnementales du quatrième trimestre.',
    },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'archived':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'environmental':
        return 'bg-blue-100 text-blue-800';
      case 'maintenance':
        return 'bg-orange-100 text-orange-800';
      case 'analysis':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rapports</h1>
          <p className="text-gray-600 mt-2">
            Générez et consultez les rapports d'analyse environnementale
          </p>
        </div>
        <button className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700 transition-colors flex items-center space-x-2">
          <Plus className="w-5 h-5" />
          <span>Nouveau rapport</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-5 h-5 text-gray-400" />
              <span className="text-sm font-medium text-gray-700">Filtres:</span>
            </div>
            <select className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="all">Tous les types</option>
              <option value="environmental">Environnemental</option>
              <option value="maintenance">Maintenance</option>
              <option value="analysis">Analyse</option>
            </select>
            <select className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500">
              <option value="all">Tous les statuts</option>
              <option value="published">Publié</option>
              <option value="draft">Brouillon</option>
              <option value="archived">Archivé</option>
            </select>
          </div>
          <div className="flex items-center space-x-2">
            <Calendar className="w-5 h-5 text-gray-400" />
            <input
              type="date"
              className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500"
            />
          </div>
        </div>
      </div>

      {/* Reports list */}
      <div className="space-y-4">
        {reports.map((report) => (
          <div key={report.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <h3 className="text-lg font-semibold text-gray-900">{report.title}</h3>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(report.type)}`}>
                    {report.type}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(report.status)}`}>
                    {report.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-3">{report.summary}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>Généré par {report.generatedBy}</span>
                  <span>•</span>
                  <span>{new Date(report.generatedAt).toLocaleDateString('fr-FR')}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                {report.downloadUrl && (
                  <button className="p-2 text-gray-400 hover:text-emerald-600 transition-colors">
                    <Download className="w-5 h-5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Reports;