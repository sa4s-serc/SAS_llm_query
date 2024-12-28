import { useState } from 'react';
import { dataState } from '../context/DataProvider';
import { cqwen, mini } from "../utils/parser";

const Aneesh = () => {
  const { data } = dataState();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showChat, setShowChat] = useState(false);
  
  const conversations = data === "cqwen" ? cqwen : mini;
  const currentConversation = conversations?.conversations[currentIndex];

  const handlePrevious = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  const handleNext = () => {
    if (currentIndex < 32) setCurrentIndex(currentIndex + 1);
  };

  if (!currentConversation) {
    return <div>Loading conversations...</div>;
  }

  return (
    <div className="p-8">
      {/* Navigation */}
      <div className="flex items-center justify-between mb-6">
        <button 
          onClick={handlePrevious}
          disabled={currentIndex === 0}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Previous
        </button>
        <span className="text-xl font-bold">
          Conversation {currentIndex + 1}
        </span>
        <button 
          onClick={handleNext}
          disabled={currentIndex === 32}
          className="px-4 py-2 bg-blue-500 text-white rounded disabled:bg-gray-300"
        >
          Next
        </button>
      </div>

      {/* Content */}
      <div className="space-y-6">
        {/* Original Query */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-3">Original Query</h2>
          <p>{currentConversation.original_goal}</p>
        </div>

        {/* Expected Services */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-3">Expected Services</h2>
          <div className="flex flex-wrap gap-2">
            {currentConversation.expected_services.map((service, idx) => (
              <span 
                key={idx}
                className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
              >
                {service}
              </span>
            ))}
          </div>
        </div>

        {/* Core Services */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-bold mb-3">Core Services</h2>
          <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded">
            {currentConversation.core_services}
          </pre>
        </div>

        {/* Show Chat Button */}
        <button
          onClick={() => setShowChat(true)}
          className="w-full py-3 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Show Full Chat
        </button>

        {/* Chat Modal */}
        {showChat && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-lg max-w-3xl w-full max-h-[80vh] overflow-y-auto">
              <div className="sticky top-0 bg-white p-4 border-b flex justify-between items-center">
                <h2 className="text-xl font-bold">Full Conversation</h2>
                <button 
                  onClick={() => setShowChat(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>
              <div className="p-4 space-y-4">
                {currentConversation.conversation.map((msg, idx) => (
                  <div 
                    key={idx}
                    className={`p-4 rounded-lg ${
                      msg.role === 'Tourist' 
                        ? 'bg-blue-50 ml-12' 
                        : 'bg-gray-50 mr-12'
                    }`}
                  >
                    <div className="font-bold mb-2">{msg.role}</div>
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Aneesh;