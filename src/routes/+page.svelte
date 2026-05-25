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
		CardTitle,
		InputGroupText
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

	async function link_available(link: string): Promise<boolean> {
		return fetch(link, { method: 'HEAD' })
			.then((res) => res.ok)
			.catch(() => false);
	}
</script>

<Card class="mt-5 flex-grow-1 mb-5">
	<CardBody>
		<CardTitle>Embeddings Search</CardTitle>
		<Form on:submit={handleSubmit}>
			<InputGroup>
				<Input type="search" placeholder="Search..." bind:value={$query} />
				{#if $dbStore == null || $results?.length == 0}
					<InputGroupText style="width: 60px; justify-content: center;"
						><Spinner size="sm" /></InputGroupText
					>
				{:else}
					<Button type="submit" disabled={$query == ''} style="width: 60px;">Go</Button>
				{/if}
			</InputGroup>
		</Form>

		{#if $results != null}
			<ListGroup class="mt-4">
				{#each $results as result (result.entry.file + result.entry.line)}
					<ListGroupItem>
						<div class="fw-bold">
							{result.entry.file}
						</div>
						<div class="text-muted" style="font-size: 0.9em;">
							{result.entry.chunk.slice(0, TEXT_CUTOFF)}...
						</div>
						<div class="badge bg-secondary mt-1">Score: {result.score.toFixed(2)}</div>
						{#if result.entry.path}
							<div style="position: absolute; top: 0.5rem; right: 0.5rem;">
								<Button
									title="Open file"
									href={result.entry.path}
									size="sm"
									type="button"
									color="primary"
								>
									<i class="bi bi-box-arrow-up-right"></i>
								</Button>
							</div>
						{/if}
					</ListGroupItem>
				{/each}
			</ListGroup>
		{/if}
	</CardBody>
</Card>
