export function formatBudget(budget: number): string {
  if (budget < 1000) {
    return `${budget}k`;
  } else {
    return `${(budget / 1000).toFixed(1)}M`;
  }
}