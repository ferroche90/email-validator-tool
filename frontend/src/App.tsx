import './App.css'
import { EmailChecker } from './components/EmailChecker'
import LanguageSwitcher from './components/LanguageSwitcher'
import CsvUploader from './components/CsvUploader'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto py-8">
        <div className="flex justify-end mb-4">
          <LanguageSwitcher />
        </div>
        <EmailChecker />
        <div className="mt-8">
          <CsvUploader />
        </div>
      </div>
    </div>
  )
}

export default App
