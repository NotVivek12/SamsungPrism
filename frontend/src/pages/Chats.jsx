import React, { useState, useEffect, useRef } from 'react';
import { Send, UserCircle } from 'lucide-react';

// Enhanced mock data for contacts
const mockContacts = [
  { 
    id: 'prof1', 
    name: 'Dr. Evelyn Reed', 
    lastMessage: 'The new publication is excellent!', 
    status: 'Online', 
    university: 'State University', 
  },
  { id: 'prof2', name: 'Professor David Lee', lastMessage: 'Thanks for the quick response.', status: 'Offline', university: 'MIT' },
  { id: 'prof3', name: 'Dr. Michael Chen', lastMessage: 'Got it. I will share the draft soon.', status: 'Online', university: 'Stanford' },
  { id: 'prof4', name: 'Dr. Jane Doe', lastMessage: 'Let\'s schedule a meeting next week.', status: 'Offline', university: 'Harvard' },
  { id: 'prof5', name: 'Dr. Sam Green', lastMessage: 'Review complete!', status: 'Online', university: 'Caltech' },
  { id: 'prof6', name: 'Professor Lee', lastMessage: 'Final report submitted.', status: 'Online', university: 'UCLA' },
];

const mockMessages = {
  prof1: [
    { id: 1, sender: 'mentor', text: 'Hi Dr. Reed, I just reviewed the latest draft of your paper. It looks great!', timestamp: '10:05 AM' },
    { id: 2, sender: 'prof', text: 'Thank you! I appreciate the feedback. Do you have any suggestions for the introduction?', timestamp: '10:06 AM' },
    { id: 3, sender: 'mentor', text: 'I think it could be more concise. I\'ll send over some tracked changes later today.', timestamp: '10:07 AM' },
    { id: 4, sender: 'prof', text: 'Sounds good. The new publication is excellent!', timestamp: '10:08 AM' },
  ],
  prof2: [
    { id: 1, sender: 'prof', text: 'Hi there! Thanks for the quick response on the grant proposal.', timestamp: 'Yesterday' },
  ],
  prof3: [
    { id: 1, sender: 'mentor', text: 'Dr. Chen, have you had a chance to look at the project timeline?', timestamp: 'Last week' },
    { id: 2, sender: 'prof', text: 'Got it. I will share the draft soon.', timestamp: 'Last week' },
  ],
  prof4: [
    { id: 1, sender: 'prof', text: 'Hello, let\'s schedule a meeting next week to discuss the new worklet.', timestamp: 'Last week' },
  ],
  prof5: [
    { id: 1, sender: 'prof', text: 'Review of the worklet is now complete. Great work!', timestamp: 'Earlier this week' },
  ],
  prof6: [
    { id: 1, sender: 'prof', text: 'The final report has been submitted to the review board.', timestamp: 'This morning' },
  ],
};

const Chats = () => {
  const [selectedContact, setSelectedContact] = useState(mockContacts[0]);
  const [messages, setMessages] = useState(mockMessages[mockContacts[0].id] || []);
  const [newMessage, setNewMessage] = useState('');

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (newMessage.trim() === '') return;

    const newMsg = {
      id: messages.length + 1,
      sender: 'mentor',
      text: newMessage,
      timestamp: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages([...messages, newMsg]);
    setNewMessage('');
  };

  const selectContact = (contactId) => {
    const contact = mockContacts.find(c => c.id === contactId);
    setSelectedContact(contact);
    setMessages(mockMessages[contactId] || []);
  };

  return (
    <div className="flex h-[75vh] text-gray-900 dark:text-gray-100 mx-auto max-w-7xl">
      {/* Sidebar for Contacts */}
      <div className="w-1/4 flex flex-col bg-white border-r border-gray-200 dark:bg-slate-800 dark:border-slate-700 p-4">
        <h2 className="text-xl font-bold mb-4">Professors</h2>
        <div className="flex-1 overflow-y-auto">
          {mockContacts.map(contact => (
            <div
              key={contact.id}
              onClick={() => selectContact(contact.id)}
              className={`flex items-center p-2 rounded-lg cursor-pointer transition-colors ${
                selectedContact.id === contact.id ? 'bg-blue-100 dark:bg-blue-900' : 'hover:bg-gray-100 dark:hover:bg-slate-700'
              }`}
            >
              <UserCircle size={32} className="text-gray-400" />
              <div className="ml-2">
                <div className="font-semibold text-sm">{contact.name}</div>
                {contact.university && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">{contact.university}</div>
                )}
                <div className="text-sm text-gray-500 dark:text-gray-400 truncate w-40">{contact.lastMessage}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Chat Window */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header with Gradient */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 border-b border-blue-700 dark:border-purple-700 text-white p-3 flex items-center shadow-sm">
          <UserCircle size={40} className="text-white opacity-80" />
          <div className="ml-3">
            <h3 className="text-lg font-semibold">{selectedContact.name}</h3>
            <span className={`text-sm ${selectedContact.status === 'Online' ? 'text-green-200' : 'text-gray-200'}`}>
              {selectedContact.university} &bull; {selectedContact.status}
            </span>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 p-4 overflow-y-auto" style={{ backgroundImage: "url('https://cdn.wallpapersafari.com/46/66/WJ4oV6.jpg')", backgroundSize: 'cover' }}>
          <div className="flex flex-col space-y-3">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.sender === 'mentor' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs p-2 rounded-xl shadow-md ${
                    msg.sender === 'mentor'
                      ? 'bg-blue-500 text-white rounded-br-none'
                      : 'bg-white dark:bg-slate-700 text-gray-800 dark:text-gray-200 rounded-bl-none'
                  }`}
                >
                  <p className="text-sm">{msg.text}</p>
                  <span className={`text-[10px] mt-1 block ${msg.sender === 'mentor' ? 'text-blue-200' : 'text-gray-500 dark:text-gray-400'}`}>
                    {msg.timestamp}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Message Input Field */}
        <form onSubmit={handleSendMessage} className="bg-white border-t border-gray-200 dark:bg-slate-800 dark:border-slate-700 p-3 flex items-center">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 py-1 px-3 text-sm rounded-full bg-gray-100 dark:bg-slate-700 border-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="ml-2 p-2 rounded-full bg-blue-500 text-white transition-colors hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chats;