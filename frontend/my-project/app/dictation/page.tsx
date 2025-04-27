"use client"
import {useEffect, useState} from "react"

// Event Target is parent of SpeechRecognition
export default function Page() {
    const [speechReg, setSpeechReg] = useState<Window["SpeechRecognition"] | null>(null);
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.lang = "en-US";
                recognition.interimResults = false;

                recognition.onresult = (event: Window["SpeechRecognitionEvent"]) => {
                    console.info(event.results);
                    const result = event.results[event.resultIndex];
                    if (result.isFinal) {
                        const transcript = result[0].transcript
                        console.log(`Speech recognized: ${transcript}`);
                    }
                };
                setSpeechReg(recognition);
            }
        }
    }, []);
  function handleMicToggle(event: React.ChangeEvent<HTMLInputElement>) {
    console.log("Handle Mic Toggle Hit")
    if (!speechReg) return;
    console.log("Speech Recognition Activated")
    
    if (event.target.checked) {
        console.log("Speech Recognition On");
      speechReg.start();
    } else {
        console.log("Speech Recognition Off");
      speechReg.stop();
    }
  }


  return (
    <div>
        Hello World!
        <label className="flex items-center gap-2 cursor-pointer select-none">
        <input type="checkbox" id="mic-toggle" className="sr-only peer" onChange={event => handleMicToggle(event)} />
        <div className="h-5 w-5 rounded border-2 border-gray-400 peer-checked:border-green-500 peer-checked:bg-green-500 relative transition">
            <svg
            className="absolute hidden peer-checked:block left-1 top-0.5 w-3 h-3 text-white"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            viewBox="0 0 24 24"
            >
            <path d="M5 13l4 4L19 7" />
            </svg>
        </div>
        <span className="text-sm text-gray-700">I agree to the terms</span>
        </label>
    </div>
  );
}
declare global { // Remove Typescript errors
    interface Window {
      webkitSpeechRecognition: any;
      SpeechRecognition: any;
      SpeechRecognitionEvent: any;
    }
}