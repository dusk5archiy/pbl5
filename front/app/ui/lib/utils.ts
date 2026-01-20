export function formatBudget(budget: number): string {
  // if (budget >= 1000) {
  //   return `${(budget / 1000).toFixed(1)}M`;
  // }
  return `${budget}k`;
}
