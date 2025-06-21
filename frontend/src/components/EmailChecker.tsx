import { useState } from 'react'
import { ArrowPathIcon, Cog6ToothIcon, DocumentArrowDownIcon } from '@heroicons/react/24/outline'
import { useValidateEmails } from '../lib/useValidateEmails'
import clsx from 'clsx'

interface ValidationResult {
  email: string
  status: string
  details?: string
}

export const EmailChecker = () => {
  const [emails, setEmails] = useState('')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [enableSmtp, setEnableSmtp] = useState(false)
  const [enableCatchAll, setEnableCatchAll] = useState(false)
  
  const { mutate, isPending, error, data } = useValidateEmails()

  const handleValidate = () => {
    const emailList = emails
      .split('\n')
      .map(email => email.trim())
      .filter(email => email.length > 0)
    
    if (emailList.length === 0) return

    mutate({
      emails: emailList,
      enable_smtp: enableSmtp,
      enable_catch_all: enableCatchAll
    })
  }

  const handleDownloadCSV = () => {
    if (!data?.results) return

    const csvContent = [
      'Email,Status,Details',
      ...data.results.map(result => 
        `"${result.email}","${result.status}","${result.details || ''}"`
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', 'email-validation-results.csv')
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'valid':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'invalid_syntax':
      case 'invalid_domain':
      case 'invalid_mx':
      case 'invalid_smtp':
      case 'disposable':
      case 'role_account':
      case 'on_bounce_list':
      case 'catch_all':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'unknown_error':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-4">Email Validator</h2>
        
        {/* Email Input */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Addresses (one per line)
          </label>
          <textarea
            value={emails}
            onChange={(e) => setEmails(e.target.value)}
            placeholder="Enter email addresses here...&#10;example@domain.com&#10;test@example.org"
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Advanced Options */}
        <div className="mb-4">
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800"
          >
            <Cog6ToothIcon className="w-4 h-4" />
            ⚙️ Avanzado
          </button>
          
          {showAdvanced && (
            <div className="mt-2 space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={enableSmtp}
                  onChange={(e) => setEnableSmtp(e.target.checked)}
                  className="mr-2"
                />
                Enable SMTP verification
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={enableCatchAll}
                  onChange={(e) => setEnableCatchAll(e.target.checked)}
                  className="mr-2"
                />
                Enable catch-all detection
              </label>
            </div>
          )}
        </div>

        {/* Validate Button */}
        <button
          onClick={handleValidate}
          disabled={isPending || !emails.trim()}
          className={clsx(
            "flex items-center gap-2 px-4 py-2 rounded-md font-medium",
            isPending || !emails.trim()
              ? "bg-gray-300 text-gray-500 cursor-not-allowed"
              : "bg-blue-600 text-white hover:bg-blue-700"
          )}
        >
          {isPending ? (
            <ArrowPathIcon className="w-4 h-4 animate-spin" />
          ) : null}
          {isPending ? 'Validating...' : 'Validar'}
        </button>

        {/* Error Display */}
        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            Error: {error.message}
          </div>
        )}
      </div>

      {/* Results Table */}
      {data?.results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Validation Results</h3>
            <button
              onClick={handleDownloadCSV}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              <DocumentArrowDownIcon className="w-4 h-4" />
              Descargar CSV
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Details
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {data.results.map((result: ValidationResult, index: number) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {result.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={clsx(
                        "inline-flex px-2 py-1 text-xs font-semibold rounded-full border",
                        getStatusColor(result.status)
                      )}>
                        {result.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500">
                      {result.details || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
} 