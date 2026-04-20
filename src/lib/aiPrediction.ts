export type PredictionResult = {
  bullishProbability: number
  bearishProbability: number
  expectedMove: string
  confidence: "Low" | "Medium" | "High"
  reasoning: string
}

export function generatePrediction(priceHistory: number[]): PredictionResult {
  const returns = priceHistory.slice(1).map((p, i) => (p - priceHistory[i]) / priceHistory[i])
  
  const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length
  const volatility = Math.sqrt(
    returns.reduce((a, b) => a + b * b, 0) / returns.length
  )

  const bullishProbability = Math.min(
    Math.max(50 + avgReturn * 500, 5),
    95
  )

  const bearishProbability = 100 - bullishProbability

  let confidence: "Low" | "Medium" | "High" = "Low"
  if (volatility < 0.005) confidence = "High"
  else if (volatility < 0.015) confidence = "Medium"

  const expectedMove = `${(avgReturn * 100).toFixed(2)}%`

  return {
    bullishProbability: Math.round(bullishProbability),
    bearishProbability: Math.round(bearishProbability),
    expectedMove,
    confidence,
    reasoning:
      avgReturn > 0
        ? "Momentum trending upward with controlled volatility."
        : "Market showing bearish momentum and weakness."
  }
}
