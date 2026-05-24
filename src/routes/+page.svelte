<script lang="ts">
	import { onMount } from 'svelte';
	import { writable } from 'svelte/store';
	import {
		Input,
		InputGroup,
		Button,
		Form,
		ListGroup,
		ListGroupItem,
		Spinner,
		Card,
		CardBody,
		CardTitle
	} from '@sveltestrap/sveltestrap';

	import { EmbedDB, type QueryResult } from '$lib/embedDB';

	let dbStore = writable<EmbedDB | null>(null);
	let results = writable<QueryResult[] | null>(null);
	let query = writable('');

	const TEXT_CUTOFF = 120;

	onMount(async () => {
		const db = await EmbedDB.load();
		dbStore.set(db);
	});

	function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		results.set([]);

		$dbStore?.search($query).then((res) => results.set(res));
	}
</script>

<Card class="mt-5 flex-grow-1 mb-5">
	<CardBody>
		<CardTitle>Embeddings Search</CardTitle>
		<Form on:submit={handleSubmit}>
			<InputGroup>
				<Input type="search" placeholder="Search..." bind:value={$query} />
				{#if $dbStore == null || $query == ''}
					<Button type="submit" disabled>Go</Button>
				{:else if $results?.length == 0}
					<Spinner />
				{:else}
					<Button type="submit">Go</Button>
				{/if}
			</InputGroup>
		</Form>

		{#if $results != null}
			<ListGroup class="mt-4">
				{#each $results as result (result.entry.file + result.entry.chunk)}
					<ListGroupItem>
						<div class="fw-bold">{result.entry.file}:{result.entry.line}</div>
						<div class="text-muted" style="font-size: 0.9em;">
							{result.entry.chunk.slice(0, TEXT_CUTOFF)}...
						</div>
						<div class="badge bg-secondary mt-1">Score: {result.score.toFixed(2)}</div>
					</ListGroupItem>
				{/each}
			</ListGroup>
		{/if}
	</CardBody>
</Card>
