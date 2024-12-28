import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/Dialogue';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';

export default function ConversationDisplay({ 
  conversations, 
  startIndex = 1, 
  endIndex = 33 
}) {
  const [currentIndex, setCurrentIndex] = useState(startIndex - 1);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const currentConversation = conversations[currentIndex];
  
  const handlePrevious = () => {
    if (currentIndex > startIndex - 1) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < endIndex - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Navigation */}
      <div className="flex justify-between items-center mb-6">
        <button 
          onClick={handlePrevious}
          disabled={currentIndex === startIndex - 1}
          className="p-2 rounded-full hover:bg-slate-200 disabled:opacity-50"
        >
          ←
        </button>
        <span className="text-lg font-semibold">
          Conversation {currentIndex + 1} of {endIndex}
        </span>
        <button 
          onClick={handleNext}
          disabled={currentIndex === endIndex - 1}
          className="p-2 rounded-full hover:bg-slate-200 disabled:opacity-50"
        >
          →
        </button>
      </div>

      {/* Main Cards */}
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Original Query</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700">{currentConversation.original_goal}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Expected Services</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {currentConversation.expected_services.map((service, index) => (
                <span 
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {service}
                </span>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Core Services</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm bg-slate-50 p-4 rounded">
              {currentConversation.core_services}
            </pre>
          </CardContent>
        </Card>

        <button 
          onClick={() => setIsDialogOpen(true)}
          className="w-full py-3 px-4 bg-slate-800 text-white rounded-lg hover:bg-slate-700 flex items-center justify-center gap-2"
        >
          💬 Show Full Chat
        </button>

        {isDialogOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div 
              className="absolute inset-0 bg-black/50"
              onClick={() => setIsDialogOpen(false)}
            />
            <div className="relative z-50 w-full max-w-3xl max-h-[80vh] overflow-y-auto bg-white rounded-lg shadow-lg m-4">
              <div className="sticky top-0 bg-white p-4 border-b">
                <h2 className="text-xl font-semibold">Full Conversation</h2>
                <button
                  onClick={() => setIsDialogOpen(false)}
                  className="absolute right-4 top-4 text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-4 p-4">
                {currentConversation.conversation.map((message, index) => (
                  <div 
                    key={index}
                    className={`p-4 rounded-lg ${
                      message.role === 'Tourist' 
                        ? 'bg-blue-50 ml-12' 
                        : 'bg-gray-50 mr-12'
                    }`}
                  >
                    <div className={`font-semibold mb-2 ${
                      message.role === 'Tourist' ? 'text-blue-800' : 'text-gray-800'
                    }`}>
                      {message.role}
                    </div>
                    <div className="text-gray-700 whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}