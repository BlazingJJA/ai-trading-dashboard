import { useState } from "react"
import { generatePrediction } from "../lib/aiPrediction"

export default function AIPrediction() {
  const [result, setResult] = useState<any>(null)

  function runPrediction() {
    // Fake price history for MVP
    const mockPrices = Array.from({ length: 100 }, () =>
      1 + Math.random() * 0.02
    )

    const prediction = generatePrediction(mockPrices)
    setResult(prediction)
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">AI Price Prediction</h1>

      <button
        onClick={runPrediction}
        className="bg-black text-white px-4 py-2 rounded"
      >
        Run Prediction
      </button>

      {result && (
        <div className="mt-6 border p-4 rounded">
          <p>Bullish Probability: {result.bullishProbability}%</p>
          <p>Bearish Probability: {result.bearishProbability}%</p>
          <p>Expected Move: {result.expectedMove}</p>
          <p>Confidence: {result.confidence}</p>
          <p className="mt-2 italic">{result.reasoning}</p>
        </div>
      )}
    </div>
  )
}
<Link to="/ai">AI Prediction</Link>
<Route path="/ai" element={<AIPrediction />} />
