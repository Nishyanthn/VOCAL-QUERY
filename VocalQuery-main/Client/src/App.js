import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css"; // Custom CSS for styling

const App = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [transcription, setTranscription] = useState("");
    const [sqlQuery, setSqlQuery] = useState("");
    const [executionResult, setExecutionResult] = useState("");
    const [loading, setLoading] = useState(false); // Loading state
    const [isConnected, setIsConnected] = useState(false); // Connection state
    const [serverStatus, setServerStatus] = useState("Checking connection..."); // Status message
    const mediaRecorderRef = useRef(null);
    const audioChunks = useRef([]);

    // Check connection to backend on component mount
    useEffect(() => {
        const checkConnection = async () => {
            try {
                const response = await axios.get("http://localhost:5000/health");
                if (response.status === 200) {
                    setIsConnected(true);
                    setServerStatus("Connected to backend server"); // Set status message
                    console.log("Connected to backend server");
                }
            } catch (error) {
                setServerStatus(); // Set status message
            }
        };

        checkConnection();
    }, []);

    // Function to start recording
    const startRecording = async () => {
        setIsRecording(true);
        setTranscription(""); // Clear previous transcription
        setSqlQuery(""); // Clear previous SQL query
        setExecutionResult(""); // Clear previous execution result

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunks.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunks.current.push(event.data);
                }
            };

            mediaRecorderRef.current.start();
        } catch (err) {
            console.error("Error accessing microphone:", err);
        }
    };

    // Function to stop recording and return the recorded Blob
    const stopRecording = () => {
        return new Promise((resolve) => {
            mediaRecorderRef.current.onstop = () => {
                const audioBlob = new Blob(audioChunks.current, { type: "audio/wav" });
                resolve(audioBlob);
            };
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        });
    };

    // Toggle recording function
    const toggleRecording = async () => {
        if (isRecording) {
            const audioBlob = await stopRecording();
            sendAudioToBackend(audioBlob);
        } else {
            startRecording();
        }
    };

    // Function to send the recorded audio to the backend
    const sendAudioToBackend = async (audioBlob) => {
        const formData = new FormData();
        formData.append("audio", audioBlob);
        formData.append("sample_rate", "16000");

        try {
            setLoading(true); // Set loading to true when sending audio
            const response = await axios.post("http://localhost:5000/transcribe_audio", formData);
            setTranscription(response.data.transcription); // Display transcription
            setSqlQuery(response.data.sql_query);
        } catch (error) {
            console.error("Error transcribing audio:", error);
        } finally {
            setLoading(false); // Reset loading state after processing
        }
    };

    // Function to execute the SQL query
    const executeQuery = async () => {
        setLoading(true);
        try {
            const response = await axios.post('http://localhost:5000/execute_query', { sql_query: sqlQuery });
            setExecutionResult(response.data.message);
        } catch (error) {
            setExecutionResult('Error executing query: ${error.response ? error.response.data.message : error.message}');
        } finally {
            setLoading(false);
        }
    };

    // Function to copy text to clipboard
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text)
            .then(() => {
                alert("Copied to clipboard!");
            })
            .catch(err => {
                console.error("Failed to copy text: ", err);
            });
    };

    return (
        <div className="app">
            <h1 className="title">Vocal Query</h1>
            <p>{serverStatus}</p> {/* Display server connection status */}
            <div className="container">
                <div className="left-side">
                    <label className="switch">
                        <input
                            type="checkbox"
                            checked={isRecording}
                            onChange={toggleRecording}
                        />
                        <span className="slider round"></span>
                    </label>
                    <div className="transcription-box">
                        <textarea
                            value={transcription}
                            onChange={(e) => setTranscription(e.target.value)} // Make text editable
                            rows={4}
                            placeholder="Your speech will appear here..."
                        />
                        <button onClick={() => copyToClipboard(transcription)} className="copy-button">📋</button>
                        {loading && <p className="loading">Generating SQL query...</p>}
                    </div>
                </div>
                <div className="right-side">
                    <div className="sql-query-box">
                        <textarea
                            value={sqlQuery}
                            onChange={(e) => setSqlQuery(e.target.value)} // Make text editable
                            rows={4}
                            placeholder="Generated SQL Query will appear here..."
                        />
                        <button onClick={() => copyToClipboard(sqlQuery)} className="copy-button">📋</button>
                    </div>
                    <button className="execute-button" onClick={executeQuery} disabled={!sqlQuery}>
                        Execute Query
                    </button>
                    {executionResult && <p className="result">{executionResult}</p>}
                </div>
            </div>
        </div>
    );
};

export default App;