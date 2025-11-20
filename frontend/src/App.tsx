import { Sidebar } from './components/Sidebar'
import { ChatArea } from './components/ChatArea'
import { ChatInput } from './components/ChatInput'

function App() {
  return (
    <div className="flex h-screen bg-neutral-50">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <ChatArea />
        <ChatInput />
      </div>
    </div>
  )
}

export default App
