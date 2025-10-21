"use client"
import {useEffect, useState} from "react"
//https://webaudio.github.io/web-speech-api/#eventdef-speechrecognition-result
//https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
//https://github.com/Riley-Brown/react-speech-to-text/issues/23
// Event Target is parent of SpeechRecognition
export default function Page() {
    const [speechReg, setSpeechReg] = useState<Window["SpeechRecognition"] | null>(null);
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList;
            const grammar =
  "#JSGF V1.0; grammar colors; public <color> = aqua | azure | beige | bisque | black | blue | brown | chocolate | coral | crimson | cyan | fuchsia | ghostwhite | gold | goldenrod | gray | green | indigo | ivory | khaki | lavender | lime | linen | magenta | maroon | moccasin | navy | olive | orange | orchid | peru | pink | plum | purple | red | salmon | sienna | silver | snow | tan | teal | thistle | tomato | turquoise | violet | white | yellow ;";
            const speechRecognitionList = new SpeechGrammarList();
            speechRecognitionList.addFromString(grammar, 1);

            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                // recognition.grammars = speechRecognitionList;
                recognition.continuous = true;
                recognition.lang = "en-US";
                recognition.interimResults = true;

                recognition.onresult = (event: Window["SpeechRecognitionEvent"]) => {
                    console.log("recognition results hit");
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
            strokeWidth="2"
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