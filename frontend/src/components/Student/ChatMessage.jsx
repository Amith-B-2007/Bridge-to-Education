import React from 'react';

export const ChatMessage = ({ message }) => {
  const isStudent = message.role === 'student';

  return (
    <div className={`flex ${isStudent ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl ${
          isStudent
            ? 'bg-gradient-to-br from-cyan-500 to-cyan-700 text-white rounded-br-sm shadow-lg shadow-cyan-200'
            : 'bg-white text-slate-800 border border-slate-200 rounded-bl-sm shadow-sm'
        }`}
      >
        <p className="break-words whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </p>
        {message.created_at && (
          <p className={`text-xs mt-1 ${isStudent ? 'text-cyan-100' : 'text-slate-400'}`}>
            {new Date(message.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </p>
        )}
      </div>
    </div>
  );
};
