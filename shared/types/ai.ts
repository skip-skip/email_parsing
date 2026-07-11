export interface ConfidenceScore {
  score: number;
  field: string;
  reasoning: string | null;
}

export interface AIDecision {
  model: string;
  prompt_version: string;
  prompt: string;
  response: string;
  parsed_json: Record<string, unknown>;
  confidence: number;
  execution_time: number;
}
