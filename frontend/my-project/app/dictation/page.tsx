"use client"
import {useEffect, useState} from "react"

export default function Page() {
    const [speechReg, setSpeechReg] = useState<any | null>(null);
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.continuous = true;
                recognition.lang = "en-US";
                recognition.interimResults = false;

                recognition.onresult = (event: any) => {
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
    if (!speechReg) return;
    
    if (event.target.checked) {
      speechReg.start();
    } else {
      speechReg.stop();
    }
  }


  return (
    <div>
        Hello World!
        <input type="checkbox" id="mic-toggle" className="sr-only" onChange={event => handleMicToggle(event)} />
    </div>
  );
}
declare global { // Remove Typescript errors
    interface Window {
      webkitSpeechRecognition: any;
      SpeechRecognition: any;
    }
}