import { useState } from "react"
import Intro from "./components/Intro"
import MainUI from "./components/MainUI"

export default function App() {
  const [showMain, setShowMain] = useState(false)
  const [mainVisible, setMainVisible] = useState(false)

  function handleIntroComplete() {
    setShowMain(true)
    setTimeout(() => setMainVisible(true), 50)
  }

  return (
    <div className="relative">
      {!showMain && <Intro onComplete={handleIntroComplete} />}

      {showMain && (
        <div
          className="transition-all duration-700"
          style={{
            transform: mainVisible ? "translateY(0)" : "translateY(40px)",
            opacity: mainVisible ? 1 : 0,
          }}
        >
          <MainUI />
        </div>
      )}
    </div>
  )
}