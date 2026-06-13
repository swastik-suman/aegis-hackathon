import React, { useState, useCallback, useEffect } from 'react';

function VoiceInterface({ onCommand, voiceResponse }) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [ttsSupported] = useState('speechSynthesis' in window);
  const [sttSupported] = useState(!!(window.SpeechRecognition || window.webkitSpeechRecognition));

  // Show latest voice response in the transcript area
  useEffect(() => {
    if (voiceResponse) {
      setTranscript('AEGIS: ' + voiceResponse);
    }
  }, [voiceResponse]);

  const startListening = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition not supported. Use Chrome or Edge.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const command = event.results[0][0].transcript;
      setTranscript(command);
      if (onCommand) onCommand(command);
    };
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognition.start();
  }, [onCommand]);

  const quickCommands = [
    { label: 'Blast Radius',   command: 'blast radius' },
    { label: 'Attack Paths',   command: 'show attack paths' },
    { label: 'Contain Threat', command: 'contain threat' },
    { label: 'Exec Brief',     command: 'executive brief' },
  ];

  const handleQuick = (cmd) => {
    setTranscript(cmd.command);
    if (onCommand) onCommand(cmd.command);
  };

  return (
    <div className="voice-interface">
      <button
        className={`voice-btn ${isListening ? 'recording' : ''}`}
        onClick={startListening}
        disabled={isListening}
        title={sttSupported ? 'Click to speak' : 'Voice not supported in this browser'}
      >
        {isListening ? '🔴' : '🎙️'}
      </button>
      <div className="voice-response">
        {isListening
          ? '🎤 Listening...'
          : transcript || 'Click mic or use quick commands below'}
      </div>
      <div className="quick-commands">
        {quickCommands.map(cmd => (
          <button
            key={cmd.command}
            className="quick-cmd-btn"
            onClick={() => handleQuick(cmd)}
          >
            {cmd.label}
          </button>
        ))}
      </div>
      {!ttsSupported && (
        <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.5rem' }}>
          ⚠️ Text-to-speech not supported in this browser
        </div>
      )}
    </div>
  );
}

export default VoiceInterface;
