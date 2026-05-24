import {
	FeatureExtractionPipeline,
	Tensor,
	cos_sim,
	pipeline,
	env
} from '@huggingface/transformers';

export type EmbedDBEntry = {
	file: string;
	line: number;
	chunk: string;
	embedding: number[];
};

export type QueryResult = {
	entry: EmbedDBEntry;
	score: number;
};

export class EmbedDB {
	private entries: EmbedDBEntry[] = [];
	private model: FeatureExtractionPipeline;

	constructor(model: FeatureExtractionPipeline, entries: EmbedDBEntry[] = []) {
		this.entries = entries;
		this.model = model;
	}

	public static async load(): Promise<EmbedDB> {
		const response = await fetch('./embeddings.json');
		if (!response.ok) {
			throw new Error('Failed to load embeddings');
		}
		const data: EmbedDBEntry[] = await response.json();

		env.allowRemoteModels = false;
		env.allowLocalModels = true;
		env.localModelPath = '';

		const model = await pipeline('feature-extraction', './model');

		return new EmbedDB(model, data);
	}

	public query(query: number[], k: number = 10): QueryResult[] {
		const results: QueryResult[] = this.entries.map((entry) => ({
			entry,
			score: cos_sim(query, entry.embedding)
		}));
		return results.sort((a, b) => b.score - a.score).slice(0, k);
	}

	public async search(query: string, k: number = 10): Promise<QueryResult[]> {
		const queryEmbedding: Tensor = await this.model(query);
		return this.query(queryEmbedding.mean(1).tolist()[0], k);
	}
}
